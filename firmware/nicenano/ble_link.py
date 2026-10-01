"""Nordic UART BLE service using CircuitPython's built-in _bleio module."""
import _bleio
import microcontroller
import time
import binascii

# Nordic UART service UUIDs, in Bluetooth little-endian byte order.
def uuid(last):
    return _bleio.UUID(bytes((0x9E, 0xCA, 0xDC, 0x24, 0x0E, 0xE5, 0xA9, 0xE0,
                              0x93, 0xF3, 0xA3, 0xB5, last, 0, 0x40, 0x6E)))

class Link:
    def __init__(self):
        self.adapter = _bleio.adapter
        self.adapter.enabled = True
        self.name = 'TrafficLight-' + binascii.hexlify(microcontroller.cpu.uid).decode()[-4:].upper()
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
        return self.buffer.read(self.buffer.in_waiting) if self.buffer.in_waiting else b''

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
