import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scripts import codex_setup
from scripts import flash_nicenano

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

class SetupTests(unittest.TestCase):
    def test_owned_hook_removal_preserves_other_handlers_in_same_group(self):
        unrelated = {'type': 'command', 'command': 'existing-tool'}
        data = {'hooks': {'Stop': [{'hooks': [unrelated, {'statusMessage': 'Traffic light: Stop'}]}]}}
        codex_setup.remove_ours(data)
        self.assertEqual(data['hooks']['Stop'][0]['hooks'], [unrelated])

    def test_firmware_rejects_wrong_board_before_downloading_or_flashing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'INFO_UF2.TXT').write_text('Board-ID: different-board')
            with patch.object(flash_nicenano, 'ROOT', root), patch.object(flash_nicenano.urllib.request, 'urlretrieve') as download:
                with self.assertRaises(RuntimeError):
                    flash_nicenano.provision(root, root / 'CIRCUITPY')
                download.assert_not_called()
                self.assertFalse((root / 'traffic.uf2').exists())

    def test_discovery_refuses_ambiguous_usb_devices(self):
        import install
        from types import SimpleNamespace
        with patch('serial.tools.list_ports.comports', return_value=[SimpleNamespace(vid=0x239A,pid=0x80B4)] * 2):
            with self.assertRaises(RuntimeError):
                install.discover_name()

class BridgeTests(unittest.TestCase):
    def test_restart_restores_current_state_and_discards_old_sessions(self):
        bridge = module('bridge')
        with tempfile.TemporaryDirectory() as directory:
            bridge.STATE_FILE = str(Path(directory) / 'sessions.json')
            bridge.active_sessions = {'live': {'state': 'Y', 'updated': time.time()},
                                      'old': {'state': 'B', 'updated': time.time() - 90000}}
            bridge.save_sessions()
            bridge.active_sessions = {}
            bridge.restore_sessions()
            self.assertEqual(bridge.current_hardware_state, 'Y')
            self.assertEqual(list(bridge.active_sessions), ['live'])

    def test_no_board_does_not_select_mac_debug_port(self):
        bridge = module('bridge')
        from types import SimpleNamespace
        debug = SimpleNamespace(device='/dev/cu.wlan-debug',description='n/a',hwid='',vid=None,pid=None)
        with patch.dict('os.environ', {}, clear=True), patch.object(bridge.serial.tools.list_ports, 'comports', return_value=[debug]):
            self.assertIsNone(bridge.find_serial_port())

    def test_input_tool_maps_to_blink_and_explicit_error_maps_to_red(self):
        traffic = module('traffic')
        for payload, expected in [({'hook_event_name':'PreToolUse','tool_name':'request_user_input_async'},'B'),
                                  ({'hook_event_name':'PostToolUse','error':'test'},'R')]:
            with patch.object(sys, 'argv', ['traffic.py']), patch.object(sys, 'stdin', io.StringIO(json.dumps({'session_id':'chat',**payload}))):
                self.assertEqual(traffic.parse_input(), ('chat',expected))

class BluetoothTests(unittest.TestCase):
    def test_fragmented_notifications_reassemble_and_ignore_invalid_lines(self):
        from ble_transport import BluetoothLink
        reports = []
        link = BluetoothLink('TrafficLight-TEST', lambda:'Y', reports.append)
        data = (json.dumps({'firmware':'traffic-nicenano-v1','mode':'Y'})+'\n').encode()
        link.notified(None, b'invalid\n'+data[:12])
        self.assertEqual(reports, [])
        link.notified(None, data[12:])
        self.assertEqual(reports[0]['mode'], 'Y')
        self.assertEqual(link.buffer, bytearray())

if __name__ == '__main__':
    unittest.main()
