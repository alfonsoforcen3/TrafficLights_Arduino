"""Persistent BLE connection to the traffic light's Nordic UART service."""
import asyncio
import json
import threading
from bleak import BleakClient, BleakScanner

SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
RX_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
TX_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

class BluetoothLink:
    def __init__(self, name, get_state, on_report):
        self.name = name
        self.get_state = get_state
        self.on_report = on_report
        self.connected = False
        self.peer = None
        self.last_error = None
        self.client = None
        self.loop = None
        self.buffer = bytearray()

    def start(self):
        threading.Thread(target=lambda: asyncio.run(self.run()), daemon=True).start()

    def notified(self, characteristic, data):
        self.buffer.extend(data)
        while b'\n' in self.buffer:
            line, _, remaining = self.buffer.partition(b'\n')
            self.buffer = bytearray(remaining)
            try:
                report = json.loads(line)
                if report.get('firmware') == 'traffic-nicenano-v1':
                    self.on_report(report)
            except (ValueError, AttributeError):
                pass
        if len(self.buffer) > 4096:
            self.buffer.clear()

    async def write(self, data):
        if not self.client or not self.client.is_connected:
            raise ConnectionError('Traffic light Bluetooth disconnected')
        await asyncio.wait_for(
            self.client.write_gatt_char(RX_UUID, data, response=True), timeout=5)

    def send(self, data):
        if not self.connected or not self.loop:
            return False
        future = asyncio.run_coroutine_threadsafe(self.write(data), self.loop)
        def done(result):
            try:
                result.result()
            except Exception as error:
                self.last_error = str(error)
                self.connected = False
                print('Bluetooth write failed: ' + str(error), flush=True)
        future.add_done_callback(done)
        return True

    async def run(self):
        self.loop = asyncio.get_running_loop()
        while True:
            try:
                print('Scanning for Bluetooth traffic light ' + self.name, flush=True)
                device = await asyncio.wait_for(BleakScanner.find_device_by_filter(
                    lambda d, a: a.local_name == self.name or d.name == self.name,
                    timeout=10, service_uuids=[SERVICE_UUID]), timeout=15)
                if not device:
                    self.last_error = 'Board not found; check that it has power'
                    await asyncio.sleep(2)
                    continue
                def disconnected(client):
                    self.connected = False
                    self.on_report(None)
                client = BleakClient(device, timeout=15, disconnected_callback=disconnected)
                self.client = client
                try:
                    await asyncio.wait_for(client.connect(), timeout=20)
                    self.buffer.clear()
                    await asyncio.wait_for(client.start_notify(TX_UUID, self.notified), timeout=10)
                    self.peer = device.address
                    self.connected = True
                    self.last_error = None
                    print('Bluetooth connected: ' + self.name + ' (' + self.peer + ')', flush=True)
                    while client.is_connected and self.connected:
                        await self.write(self.get_state().encode())
                        await asyncio.sleep(3)
                finally:
                    try:
                        await asyncio.wait_for(client.disconnect(), timeout=5)
                    except Exception:
                        pass
            except Exception as error:
                self.last_error = str(error) or type(error).__name__
                print('Bluetooth connection error: ' + str(error), flush=True)
            finally:
                self.connected = False
                self.client = None
                self.on_report(None)
            await asyncio.sleep(3)
