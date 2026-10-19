"""Explicit BLE discovery/identity transactions; no hooks, provisioning, or pairing.

A UID check prevents accidental rename of another selected board. Nordic UART
is not an authenticated ownership protocol: proximity is not proof of ownership.
Bleak is imported lazily so offline setup previews need no BLE dependencies.
"""
import asyncio
import json
import re
import unicodedata

RX_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
TX_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
SUPPORTED_FIRMWARE = ('traffic-nicenano-v1', 'traffic-esp32c3-v1')


def make_device_name(laptop, nickname, device_id):
    """29-byte legacy scan-response budget, keeping both names and UID suffix."""
    if not re.fullmatch(r'[0-9a-fA-F]{8,64}', device_id or ''):
        raise ValueError('A verified device UID is required to generate a name')
    def clean(value):
        value = unicodedata.normalize('NFKC', value).strip()
        value = ''.join(c for c in value if not unicodedata.category(c).startswith('C'))
        return re.sub(r'\s+', '-', value) or 'Clody'
    def trim(value, budget):
        return value.encode('utf-8')[:budget].decode('utf-8', errors='ignore')
    # Reserve at least nine bytes for each human component, redistribute unused bytes.
    left, right = clean(laptop), clean(nickname)
    left = trim(left, min(9, len(left.encode('utf-8'))))
    right = trim(right, 19 - len(left.encode('utf-8')))
    return '{}-{}-{}'.format(left, right, device_id[-8:].upper())


async def discover_candidates(timeout=8.0):
    from bleak import BleakScanner
    discovered = await BleakScanner.discover(timeout=timeout, return_adv=True)
    candidates = []
    for device, advert in discovered.values():
        name = advert.local_name or device.name or ''
        services = [s.lower() for s in advert.service_uuids]
        if SERVICE_UUID in services:
            candidates.append({'name': name, 'address': device.address, 'rssi': advert.rssi})
    return sorted(candidates, key=lambda item: (item['name'], item['address']))


async def _with_bounded_client(address, operation, timeout, cleanup=None):
    """Bound connect/exchange and, separately, disconnect, including failed connects.

    Bleak's context manager exit is not necessarily covered by its constructor's
    connection timeout. Keep cleanup outside the exchange deadline and preserve
    the original error if cleanup also fails. Backends must honor cancellation.
    """
    from bleak import BleakClient
    client = BleakClient(address, timeout=timeout)
    failed = False
    async def exchange():
        await client.connect()
        return await operation(client)
    try:
        return await asyncio.wait_for(exchange(), timeout=timeout)
    except BaseException:
        failed = True
        raise
    finally:
        cleanup_error = None
        if cleanup is not None:
            try:
                await asyncio.wait_for(cleanup(client), timeout=timeout)
            except Exception as error:
                cleanup_error = error
        try:
            await asyncio.wait_for(client.disconnect(), timeout=timeout)
        except Exception as error:
            if cleanup_error is None:
                cleanup_error = error
        if not failed and cleanup_error is not None:
            raise cleanup_error


async def _transaction(address, wire, predicate, timeout):
    pending = bytearray()
    loop = asyncio.get_running_loop()
    reply = loop.create_future()
    def receive(_sender, data):
        pending.extend(data)
        while b'\n' in pending:
            line, _, rest = pending.partition(b'\n')
            pending[:] = rest
            try:
                report = json.loads(line.decode('utf-8'))
            except (ValueError, UnicodeError):
                continue
            if isinstance(report, dict) and predicate(report) and not reply.done():
                reply.set_result(report)
        if len(pending) > 8192:
            pending.clear()
    async def run(client):
        await client.start_notify(TX_UUID, receive)
        for offset in range(0, len(wire), 20):
            await client.write_gatt_char(RX_UUID, wire[offset:offset + 20], response=True)
        return await reply
    return await _with_bounded_client(address, run, timeout)


async def inspect_device(address, timeout=12.0):
    report = await _transaction(address, b'Q', lambda r: r.get('transport') == 'ble' and
                                r.get('firmware') in SUPPORTED_FIRMWARE, timeout)
    return report


async def rename_device(address, name, expected_device_id, timeout=12.0):
    if not isinstance(name, str) or not 1 <= len(name.encode('utf-8')) <= 29 or any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError('Name must fit 1-29 UTF-8 bytes without controls')
    # Caller must inspect capabilities first; sending extended frames to old
    # firmware could interpret their letters as legacy colour commands.
    report = await inspect_device(address, timeout=timeout)
    if report.get('device_id') != expected_device_id:
        raise ValueError('Selected device identity changed')
    if report.get('identity_protocol') != 1 or not report.get('rename_supported'):
        raise ValueError('Firmware does not support persistent Bluetooth rename')
    wire = ('!' + json.dumps({'op': 'rename', 'name': name, 'device_id': expected_device_id},
                             ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    ack = await _transaction(address, wire, lambda r: r.get('identity_ack') == 'rename' and
                             r.get('device_id') == expected_device_id, timeout)
    if not ack.get('ok') or not ack.get('persistent') or ack.get('ble_name') != name:
        raise ValueError(ack.get('error', 'Rename was not persistently acknowledged'))
    return ack


async def identify_device(address, expected_device_id=None, timeout=12.0):
    """Brief acknowledged LED identification, restoring the selected board's state.

    The caller must obtain human confirmation before configuring this unit.
    Existing firmware without UID can be identified by its explicitly selected
    BLE address; it cannot be persistently renamed through this helper.
    """
    report = await inspect_device(address, timeout=timeout)
    if expected_device_id is not None and report.get('device_id') != expected_device_id:
        raise ValueError('Selected device identity changed')
    device_id = report.get('device_id')
    restore = report.get('mode', 'O')
    if restore not in ('R', 'Y', 'G', 'B', 'O') or report.get('display_phase') == 'searching':
        restore = 'O'

    await _identify_sequence(address, device_id, restore, timeout)
    return report


async def _identify_sequence(address, device_id, restore, timeout):
    """One connection; timeout bounds exchange, restore and disconnect separately.

    Recheck Q/UID on this connection before changing LEDs. A failed/partial LED
    write still needs a restore attempt, but failed identity/notification setup
    must not trigger one. Cleanup failures must not replace the original error.
    """
    pending = bytearray()
    responses = asyncio.Queue()
    def receive(_sender, data):
        pending.extend(data)
        while b'\n' in pending:
            line, _, rest = pending.partition(b'\n')
            pending[:] = rest
            try:
                response = json.loads(line.decode('utf-8'))
                if isinstance(response, dict):
                    responses.put_nowait(response)
            except (ValueError, UnicodeError):
                pass
        if len(pending) > 8192:
            pending.clear()
    mutated = False
    command = None
    async def run(client):
        nonlocal mutated, command
        await client.start_notify(TX_UUID, receive)
        async def send_command(mode, check_identity=True):
            # Discard earlier unsolicited/animation reports before this write.
            while not responses.empty():
                responses.get_nowait()
            await client.write_gatt_char(RX_UUID, mode.encode('ascii'), response=True)
            async def acknowledged():
                while True:
                    response = await responses.get()
                    if (response.get('transport') == 'ble'
                            and response.get('firmware') in SUPPORTED_FIRMWARE
                            and (mode == 'Q' or response.get('mode') == mode)
                            and (not check_identity or device_id is None or response.get('device_id') == device_id)):
                        return response
            return await asyncio.wait_for(acknowledged(), timeout)
        command = send_command
        report = await command('Q', check_identity=False)
        if device_id is not None and report.get('device_id') != device_id:
            raise ValueError('Selected device identity changed')
        # Existing nRF connection animation lasts about one second. Keep
        # the link alive so every requested colour becomes physically visible.
        await asyncio.sleep(1.2)
        for mode in ('R', 'Y', 'G'):
            mutated = True
            await command(mode)
            await asyncio.sleep(0.6)
    async def cleanup(client):
        if mutated:
            await command(restore)
    await _with_bounded_client(address, run, timeout, cleanup)
