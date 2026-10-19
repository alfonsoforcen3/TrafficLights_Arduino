import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import device_identity


def firmware_module():
    spec = importlib.util.spec_from_file_location('identity_ble_test', ROOT / 'firmware/nicenano/ble_link.py')
    module = importlib.util.module_from_spec(spec)
    mcu = types.SimpleNamespace(nvm=bytearray(40), cpu=types.SimpleNamespace(uid=b'12345678'))
    with patch.dict(sys.modules, {'_bleio': types.SimpleNamespace(), 'microcontroller': mcu}):
        spec.loader.exec_module(module)
    return module, mcu


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.module, self.mcu = firmware_module()
        self.link = self.module.Link.__new__(self.module.Link)
        self.link.device_id = '1234567890ABCDEF'
        self.link.name = 'Factory'
        self.link.rename_supported = True
        self.link.adapter = types.SimpleNamespace(name='Factory')
        self.acks = []
        self.link.send = lambda data: self.acks.append(json.loads(data))

    def request(self, **kwargs):
        data = dict(op='rename', device_id=self.link.device_id, name='Laptop-Pet-90ABCDEF')
        data.update(kwargs)
        self.link.identity_request(json.dumps(data).encode())
        return self.acks[-1]

    def test_persist_and_duplicate_no_write_change(self):
        self.assertTrue(self.request()['persistent'])
        stored = bytes(self.mcu.nvm)
        self.assertEqual(stored[:4], b'CLN1')
        self.assertEqual(self.request()['ble_name'], 'Laptop-Pet-90ABCDEF')
        self.assertEqual(bytes(self.mcu.nvm), stored)
        self.assertEqual(self.link.scan_response[1], 9)

    def initialize_link(self):
        class UUID:
            def __init__(self, value): self.uuid128 = value
        class Characteristic:
            WRITE, WRITE_NO_RESPONSE, NOTIFY, READ = 1, 2, 4, 8
            @staticmethod
            def add_to_service(*args, **kwargs): return object()
        self.module._bleio = types.SimpleNamespace(
            adapter=types.SimpleNamespace(), UUID=UUID,
            Service=lambda value: object(), Characteristic=Characteristic,
            CharacteristicBuffer=lambda *args, **kwargs: object())
        return self.module.Link()

    def test_name_survives_new_firmware_link_instance(self):
        self.request()
        restored = self.initialize_link()
        self.assertEqual(restored.name, 'Laptop-Pet-90ABCDEF')
        self.assertTrue(restored.rename_supported)

    def test_foreign_nvm_is_not_overwritten_and_erased_nvm_is_supported(self):
        self.mcu.nvm[:] = b'OTHER' + bytes(35)
        self.assertFalse(self.initialize_link().rename_supported)
        self.mcu.nvm[:] = b'\xff' * 40
        self.assertTrue(self.initialize_link().rename_supported)

    def test_wrong_unit_cannot_rename(self):
        self.assertFalse(self.request(device_id='other')['ok'])
        self.assertFalse(any(self.mcu.nvm))

    def test_invalid_names_and_unavailable_persistence(self):
        for value in ('x' * 30, 'pet\nR', '', '🐱' * 8):
            self.assertFalse(self.request(name=value)['ok'])
        self.link.rename_supported = False
        self.assertFalse(self.request()['ok'])
        self.assertEqual(self.link.name, 'Factory')

    def test_utf8_composed_name_has_room_for_both_names_and_suffix(self):
        for laptop, nickname in [('Alfonso MacBook', 'Clody'), ('电脑电脑电脑电脑电脑', '🐱🐱🐱🐱')]:
            name = device_identity.make_device_name(laptop, nickname, self.link.device_id)
            self.assertLessEqual(len(name.encode()), 29)
            self.assertTrue(name.endswith('-90ABCDEF'))
            self.assertEqual(len(name.split('-')[-1]), 8)

    def test_old_firmware_rejected_before_extended_wire(self):
        async def run():
            with patch.object(device_identity, 'inspect_device', return_value={'device_id': self.link.device_id}), patch.object(device_identity, '_transaction') as transaction:
                with self.assertRaisesRegex(ValueError, 'does not support'):
                    await device_identity.rename_device('chosen', 'Pet', self.link.device_id)
                transaction.assert_not_called()
        asyncio.run(run())

    def test_identify_sequence_keeps_one_connection_and_restores_on_failure(self):
        async def run(fail):
            sent, connections = [], []
            uid = self.link.device_id
            class Client:
                def __init__(self, address, timeout): connections.append(address)
                async def connect(self): pass
                async def disconnect(self): pass
                async def start_notify(self, uuid, receive): self.receive = receive
                async def write_gatt_char(self, uuid, wire, response):
                    sent.append(wire)
                    if fail and wire == b'R':
                        raise OSError('Disconnected')
                    data = dict(firmware='traffic-nicenano-v1', transport='ble', device_id=uid, mode=wire.decode())
                    self.receive(None, (json.dumps(data) + '\n').encode())
            with patch.dict(sys.modules, {'bleak': types.SimpleNamespace(BleakClient=Client)}), patch.object(device_identity.asyncio, 'sleep'):
                if fail:
                    with self.assertRaises(OSError):
                        await device_identity._identify_sequence('chosen', uid, 'B', 1)
                    self.assertEqual(sent, [b'Q', b'R', b'B'])
                else:
                    await device_identity._identify_sequence('chosen', uid, 'B', 1)
                    self.assertEqual(sent, [b'Q', b'R', b'Y', b'G', b'B'])
            self.assertEqual(connections, ['chosen'])
        asyncio.run(run(False))
        asyncio.run(run(True))

    def test_identify_stalled_backend_stages_are_bounded_and_cleanup_runs(self):
        async def run(stage):
            sent, cancelled, disconnects = [], [], []
            uid = self.link.device_id
            async def stall(label):
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.append(label)
            class Client:
                def __init__(self, address, timeout): pass
                async def connect(self):
                    if stage == 'connect': await stall(stage)
                async def disconnect(self):
                    disconnects.append(True)
                    if stage == 'disconnect': await stall(stage)
                async def start_notify(self, uuid, receive):
                    self.receive = receive
                    if stage == 'notify': await stall(stage)
                async def write_gatt_char(self, uuid, wire, response):
                    sent.append(wire)
                    if ((stage == 'query' and wire == b'Q') or
                            (stage == 'write' and wire == b'R') or
                            (stage == 'restore' and wire == b'B')):
                        await stall(stage)
                    if stage == 'ack' and wire == b'R': return
                    data = dict(firmware='traffic-nicenano-v1', transport='ble',
                                device_id=uid, mode='B' if wire == b'Q' else wire.decode())
                    self.receive(None, (json.dumps(data) + '\n').encode())
            with patch.dict(sys.modules, {'bleak': types.SimpleNamespace(BleakClient=Client)}), patch.object(device_identity.asyncio, 'sleep'):
                # Allow scheduler jitter on loaded CI: 200 ms per production-style
                # stage deadline, with a separate generous 3 s regression guard.
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(device_identity._identify_sequence('chosen', uid, 'B', 0.2), 3.0)
            self.assertEqual(disconnects, [True])
            if stage != 'ack': self.assertIn(stage, cancelled)
            if stage in ('connect', 'notify'): self.assertEqual(sent, [])
            elif stage == 'query': self.assertEqual(sent, [b'Q'])
            else: self.assertEqual(sent[-1], b'B')
        for stage in ('connect', 'notify', 'query', 'write', 'ack', 'restore', 'disconnect'):
            with self.subTest(stage=stage): asyncio.run(run(stage))

    def test_identify_rechecks_uid_on_identification_connection_before_led_write(self):
        async def run():
            sent, disconnects = [], []
            class Client:
                def __init__(self, address, timeout): pass
                async def connect(self): pass
                async def disconnect(self): disconnects.append(True)
                async def start_notify(self, uuid, receive): self.receive = receive
                async def write_gatt_char(self, uuid, wire, response):
                    sent.append(wire)
                    self.receive(None, (json.dumps(dict(firmware='traffic-nicenano-v1',
                        transport='ble', device_id='OTHER', mode='O')) + '\n').encode())
            with patch.dict(sys.modules, {'bleak': types.SimpleNamespace(BleakClient=Client)}):
                with self.assertRaisesRegex(ValueError, 'identity changed'):
                    await device_identity._identify_sequence('chosen', self.link.device_id, 'B', 0.1)
            self.assertEqual(sent, [b'Q'])
            self.assertEqual(disconnects, [True])
        asyncio.run(run())

    def test_inspect_stalled_backend_stages_are_bounded(self):
        async def run(stage):
            disconnects, sent = [], []
            class Client:
                def __init__(self, address, timeout): pass
                async def connect(self):
                    if stage == 'connect': await asyncio.Event().wait()
                async def disconnect(self):
                    disconnects.append(True)
                    if stage == 'disconnect': await asyncio.Event().wait()
                async def start_notify(self, uuid, receive):
                    self.receive = receive
                    if stage == 'notify': await asyncio.Event().wait()
                async def write_gatt_char(self, uuid, wire, response):
                    sent.append(wire)
                    if stage == 'write': await asyncio.Event().wait()
                    if stage == 'ack': return
                    self.receive(None, b'{"firmware":"traffic-nicenano-v1","transport":"ble"}\n')
            with patch.dict(sys.modules, {'bleak': types.SimpleNamespace(BleakClient=Client)}):
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(device_identity.inspect_device('chosen', timeout=0.2), 3.0)
            self.assertEqual(disconnects, [True])
            self.assertEqual(sent, [] if stage in ('connect', 'notify') else [b'Q'])
        for stage in ('connect', 'notify', 'write', 'ack', 'disconnect'):
            with self.subTest(stage=stage): asyncio.run(run(stage))

    def test_identify_cleanup_failures_preserve_initial_error(self):
        async def run():
            sent, disconnects = [], []
            uid = self.link.device_id
            class Client:
                def __init__(self, address, timeout): pass
                async def connect(self): pass
                async def disconnect(self):
                    disconnects.append(True)
                    raise OSError('Cleanup disconnect failure')
                async def start_notify(self, uuid, receive): self.receive = receive
                async def write_gatt_char(self, uuid, wire, response):
                    sent.append(wire)
                    if wire == b'R': raise OSError('Original write failure')
                    if wire == b'B': await asyncio.Event().wait()
                    self.receive(None, (json.dumps(dict(firmware='traffic-nicenano-v1',
                        transport='ble', device_id=uid, mode='B')) + '\n').encode())
            with patch.dict(sys.modules, {'bleak': types.SimpleNamespace(BleakClient=Client)}), patch.object(device_identity.asyncio, 'sleep'):
                with self.assertRaisesRegex(OSError, 'Original write failure'):
                    await asyncio.wait_for(device_identity._identify_sequence('chosen', uid, 'B', 0.2), 3.0)
            self.assertEqual(sent, [b'Q', b'R', b'B'])
            self.assertEqual(disconnects, [True])
        asyncio.run(run())

    def test_identify_wrong_uid_sends_nothing_and_restores_searching_to_off(self):
        async def run():
            report = dict(device_id=self.link.device_id, mode='Y', display_phase='searching')
            with patch.object(device_identity, 'inspect_device', return_value=report), patch.object(device_identity, '_identify_sequence') as sequence:
                with self.assertRaisesRegex(ValueError, 'identity changed'):
                    await device_identity.identify_device('chosen', 'other')
                sequence.assert_not_called()
                await device_identity.identify_device('chosen', self.link.device_id)
                sequence.assert_awaited_once_with('chosen', self.link.device_id, 'O', 12.0)
        asyncio.run(run())

    def test_fragmented_frame_does_not_execute_payload(self):
        self.link.identity_pending = None
        self.link.identity_overflow = False
        self.link.adapter.connections = [types.SimpleNamespace(connected=True)]
        wire = b'!{"op":"rename","device_id":"1234567890ABCDEF","name":"RED"}\nQ'
        class Buffer:
            def __init__(self, data): self.data = data
            @property
            def in_waiting(self): return len(self.data)
            def read(self, _size):
                data, self.data = self.data, b''
                return data
        output = bytearray()
        for start in range(0, len(wire), 7):
            self.link.buffer = Buffer(wire[start:start + 7])
            output.extend(self.link.poll())
        self.assertEqual(output, b'Q')
        self.assertTrue(self.acks[-1]['ok'])

if __name__ == '__main__':
    unittest.main()
