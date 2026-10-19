"""Nordic UART BLE service using CircuitPython's built-in _bleio module."""
import _bleio
import microcontroller
import time
import binascii
import json

# Nordic UART service UUIDs, in Bluetooth little-endian byte order.
def uuid(last):
    return _bleio.UUID(bytes((0x9E, 0xCA, 0xDC, 0x24, 0x0E, 0xE5, 0xA9, 0xE0,
                              0x93, 0xF3, 0xA3, 0xB5, last, 0, 0x40, 0x6E)))

class Link:
    def __init__(self):
        self.device_id = binascii.hexlify(microcontroller.cpu.uid).decode().upper()
        self.identity_pending = None
        self.identity_overflow = False
        self.adapter = _bleio.adapter
        self.adapter.enabled = True
        self.name = 'TrafficLight-' + binascii.hexlify(microcontroller.cpu.uid).decode()[-4:].upper()
        try:
            with open('/hardware_config.json') as config_file:
                configured_name = json.load(config_file).get('ble_name')
            if configured_name is not None:
                if not isinstance(configured_name, str) or not 1 <= len(configured_name.encode()) <= 29:
                    raise ValueError('Bluetooth name must be 1 to 29 UTF-8 bytes')
                self.name = configured_name
        except OSError:
            pass
        # NVM survives resets even when CIRCUITPY is host-owned/read-only.
        # Only an empty region or our own record is writable; never overwrite foreign data.
        # An interrupted first write may look foreign; factory-only recovery is
        # documented in docs/NRF_RENAME_RECOVERY.md. Never auto-erase unknown NVM.
        self.rename_supported = False
        try:
            record = bytes(microcontroller.nvm[:40])
            self.rename_supported = len(record) == 40 and (record[:4] == b'CLN1' or not any(record) or record == b'\xff' * 40)
            if record[:4] == b'CLN1':
                length = record[4]
                payload = record[5:5 + length]
                if 1 <= length <= 29 and sum(payload) % 256 == record[34]:
                    stored_name = payload.decode('utf-8')
                    if self.valid_name(stored_name):
                        self.name = stored_name
        except (AttributeError, OSError, ValueError, UnicodeError):
            pass
        self.adapter.name = self.name
        self.service = _bleio.Service(uuid(1))
        self.rx = _bleio.Characteristic.add_to_service(
            self.service, uuid(2), properties=_bleio.Characteristic.WRITE |
            _bleio.Characteristic.WRITE_NO_RESPONSE, max_length=20)
        self.tx = _bleio.Characteristic.add_to_service(
            self.service, uuid(3), properties=_bleio.Characteristic.NOTIFY |
            _bleio.Characteristic.READ, max_length=20)
        self.buffer = _bleio.CharacteristicBuffer(self.rx, timeout=0, buffer_size=256)
        self.advertisement = b'\x02\x01\x06\x11\x07' + bytes(uuid(1).uuid128)
        name = self.name.encode()
        self.scan_response = bytes((len(name) + 1, 9)) + name

    @property
    def connected(self):
        return any(c.connected for c in self.adapter.connections)

    def poll(self):
        if not self.connected and not self.adapter.advertising:
            self.adapter.start_advertising(self.advertisement,
                                           scan_response=self.scan_response)
        if not self.connected:
            self.identity_pending = None
            self.identity_overflow = False
        raw = self.buffer.read(self.buffer.in_waiting) if self.buffer.in_waiting else b''
        commands = bytearray()
        for value in raw:
            if self.identity_pending is not None:
                if value == 10:
                    if not self.identity_overflow:
                        self.identity_request(self.identity_pending)
                    self.identity_pending = None
                    self.identity_overflow = False
                elif len(self.identity_pending) < 192:
                    self.identity_pending.append(value)
                else:
                    self.identity_overflow = True
            elif value == 33:  # ! JSON identity frame; do not leak payload as LED commands.
                self.identity_pending = bytearray()
            else:
                commands.append(value)
        return commands

    @staticmethod
    def valid_name(name):
        return (isinstance(name, str) and 1 <= len(name.encode('utf-8')) <= 29
                and all(ord(c) >= 32 and ord(c) != 127 for c in name))

    def identity_request(self, payload):
        ack = {'identity_ack': 'rename', 'ok': False, 'persistent': False,
               'device_id': self.device_id, 'ble_name': self.name}
        try:
            request = json.loads(bytes(payload).decode('utf-8'))
            if request.get('op') != 'rename' or request.get('device_id') != self.device_id:
                raise ValueError('Selected device identity does not match')
            name = request.get('name')
            if not self.valid_name(name):
                raise ValueError('Name requires 1-29 UTF-8 bytes without control characters')
            if not self.rename_supported:
                raise ValueError('Persistent rename unavailable; update firmware at factory')
            data = name.encode('utf-8')
            record = b'CLN1' + bytes((len(data),)) + data + bytes(29 - len(data))
            record += bytes((sum(data) % 256,)) + bytes(5)
            if bytes(microcontroller.nvm[:40]) != record:
                microcontroller.nvm[:40] = record
            if bytes(microcontroller.nvm[:40]) != record:
                raise OSError('Persistent rename verification failed')
            self.adapter.name = name
            self.name = name
            self.scan_response = bytes((len(data) + 1, 9)) + data
            ack.update(ok=True, persistent=True, ble_name=name)
        except (ValueError, OSError, UnicodeError, AttributeError, TypeError) as error:
            ack['error'] = str(error)
        self.send((json.dumps(ack) + '\n').encode('utf-8'))

    def send(self, data):
        if not self.connected:
            return
        for i in range(0, len(data), 20):
            deadline = time.monotonic() + 0.2
            while self.connected:
                try:
                    self.tx.value = data[i:i + 20]
                    break
                except _bleio.BluetoothError:
                    if time.monotonic() >= deadline:
                        return
                    time.sleep(0.01)
