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
    def test_gemini_and_cursor_merge_and_removal_preserve_unrelated_hooks(self):
        from scripts import provider_setup
        for provider in ('gemini','cursor'):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                settings = root/'settings.json'
                other = {'command':'other-tool'}
                hooks = [other] if provider == 'cursor' else [{'hooks':[dict(other,name='other')]}]
                event = 'stop' if provider == 'cursor' else 'AfterAgent'
                original = {'version':1,'hooks':{event:hooks}} if provider == 'cursor' else {'theme':'custom','hooks':{event:hooks}}
                settings.write_text(json.dumps(original))
                python = provider_setup.venv_python(root); python.parent.mkdir(parents=True); python.touch()
                with patch.object(provider_setup,'settings_path',return_value=settings), patch.object(provider_setup,'RUNTIME',root), patch.object(provider_setup,'ROOT',root):
                    provider_setup.configure(provider)
                    first = json.loads(settings.read_text())
                    provider_setup.configure(provider)
                    self.assertEqual(json.loads(settings.read_text()),first)
                    provider_setup.configure(provider,False)
                    self.assertEqual(json.loads(settings.read_text()),original)

    def test_disabled_gemini_hooks_are_not_overridden(self):
        from scripts import provider_setup
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'settings.json'
            original = '{"hooksConfig":{"enabled":false}}'
            path.write_text(original)
            with patch.object(provider_setup,'settings_path',return_value=path):
                with self.assertRaises(RuntimeError): provider_setup.configure('gemini')
            self.assertEqual(path.read_text(),original)

    def test_detection_uses_executables_and_ignores_empty_gemini_folder(self):
        from scripts import provider_setup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'.gemini').mkdir()
            with patch.object(Path,'home',return_value=root), patch.object(provider_setup.shutil,'which',side_effect=lambda name:'/tools/'+name if name in ('claude','cursor-agent') else None):
                found = provider_setup.detect()
                self.assertIn('claude',found); self.assertIn('cursor',found)
                self.assertNotIn('gemini',found)

    def test_claude_install_is_idempotent_and_disable_preserves_other_settings(self):
        from scripts import claude_setup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = root / 'settings.json'
            other = {'type':'command','command':'other-tool'}
            original = {'permissions':{'allow':['Read']}, 'hooks':{'Stop':[{'hooks':[other]}]}}
            settings.write_text(json.dumps(original))
            python = claude_setup.venv_python(root)
            python.parent.mkdir(parents=True)
            python.touch()
            with patch.object(claude_setup,'SETTINGS',settings), patch.object(claude_setup,'RUNTIME',root), patch.object(claude_setup,'ROOT',root):
                claude_setup.configure(True)
                first = json.loads(settings.read_text())
                claude_setup.configure(True)
                self.assertEqual(json.loads(settings.read_text()), first)
                claude_setup.configure(False)
                self.assertEqual(json.loads(settings.read_text()), original)

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
    def test_observer_output_does_not_forward_prompt_or_approve_tools(self):
        traffic = module('traffic')
        for provider, flag, event, expected in [('claude','--silent','UserPromptSubmit',''),
                                                ('cursor','--cursor-prompt','beforeSubmitPrompt','{"continue": true}\n')]:
            out = io.StringIO()
            payload = {'session_id':'a','conversation_id':'a','hook_event_name':event,'prompt':'private prompt'}
            with patch.object(sys,'argv',['traffic.py','Y','--provider',provider,flag]), patch.object(sys,'stdin',io.StringIO(json.dumps(payload))), patch.object(sys,'stdout',out), patch.object(traffic,'send_via_tcp',return_value=(True,'ok')) as send, patch.object(traffic,'log'):
                with self.assertRaises(SystemExit): traffic.main()
                send.assert_called_once_with(provider+':a','Y')
                self.assertEqual(out.getvalue(),expected)

    def test_gemini_and_cursor_payload_mapping(self):
        traffic = module('traffic')
        cases = [('gemini',{'session_id':'a','hook_event_name':'BeforeAgent'},'gemini:a','Y'),
                 ('gemini',{'session_id':'a','hook_event_name':'AfterAgent'},'gemini:a','G'),
                 ('gemini',{'session_id':'a','hook_event_name':'Notification','notification_type':'ToolPermission'},'gemini:a','B'),
                 ('gemini',{'session_id':'a','hook_event_name':'Notification','notification_type':'info'},'gemini:a',None),
                 ('cursor',{'conversation_id':'a','hook_event_name':'beforeSubmitPrompt'},'cursor:a','Y'),
                 ('cursor',{'conversation_id':'a','hook_event_name':'stop','status':'error'},'cursor:a','R'),
                 ('cursor',{'conversation_id':'a','hook_event_name':'stop','status':'completed'},'cursor:a','G')]
        for provider,payload,sid,state in cases:
            with patch.object(sys,'argv',['traffic.py','--provider',provider]), patch.object(sys,'stdin',io.StringIO(json.dumps(payload))):
                self.assertEqual(traffic.parse_input(),(sid,state))

    def test_same_chat_id_is_separate_across_providers(self):
        traffic = module('traffic')
        results = []
        for provider in ('codex','claude'):
            with patch.object(sys,'argv',['traffic.py','Y','--provider',provider]), patch.object(sys,'stdin',io.StringIO('{"session_id":"same","hook_event_name":"UserPromptSubmit"}')):
                results.append(traffic.parse_input())
        self.assertEqual(results, [('codex:same','Y'),('claude:same','Y')])
        bridge = module('bridge')
        bridge.active_sessions = {sid:{'state':state} for sid,state in results}
        bridge.active_sessions['claude:same']['state'] = 'G'
        self.assertEqual(bridge.compute_aggregate_state(),'Y')

    def test_claude_error_and_question_lifecycle(self):
        traffic = module('traffic')
        for payload, state in [({'hook_event_name':'StopFailure'},'R'),
                               ({'hook_event_name':'PostToolUseFailure','error':'command failed'},'Y'),
                               ({'hook_event_name':'PreToolUse','tool_name':'AskUserQuestion'},'B'),
                               ({'hook_event_name':'PostToolUse','tool_name':'AskUserQuestion'},'Y')]:
            with patch.object(sys,'argv',['traffic.py','--provider','claude']), patch.object(sys,'stdin',io.StringIO(json.dumps({'session_id':'chat',**payload}))):
                self.assertEqual(traffic.parse_input(), ('claude:chat',state))

    def test_multiple_chats_follow_priority_without_losing_other_sessions(self):
        bridge = module('bridge')
        for states, expected in [(('Y','G'),'Y'), (('G','Y'),'Y'), (('Y','R'),'R'),
                                 (('R','B'),'B'), (('G','G'),'G')]:
            bridge.active_sessions = {str(i): {'state': state, 'updated':time.time()}
                                      for i, state in enumerate(states)}
            self.assertEqual(bridge.compute_aggregate_state(), expected)
        bridge.active_sessions = {'working': {'state':'Y'}, 'finished': {'state':'G'}}
        del bridge.active_sessions['finished']
        self.assertEqual(bridge.compute_aggregate_state(), 'Y')
        bridge.active_sessions.clear()
        self.assertEqual(bridge.compute_aggregate_state(), 'G')

    def test_green_waits_for_completion_and_resumed_work_cancels_it(self):
        bridge = module('bridge')
        bridge.current_hardware_state = 'Y'
        with patch.object(bridge.time, 'monotonic', return_value=10), patch.object(bridge, 'write_to_hardware') as write:
            bridge.request_transition('G')
            bridge.settle_transition()
            write.assert_not_called()
            bridge.request_transition('Y')
            self.assertIsNone(bridge.pending_transition)
        with patch.object(bridge.time, 'monotonic', return_value=20):
            bridge.request_transition('G')
        with patch.object(bridge.time, 'monotonic', return_value=21.6), patch.object(bridge, 'write_to_hardware') as write:
            bridge.settle_transition()
            write.assert_called_once_with('G')

    def test_brief_input_signal_does_not_flash_red(self):
        bridge = module('bridge')
        bridge.current_hardware_state = 'Y'
        with patch.object(bridge.time, 'monotonic', return_value=10), patch.object(bridge, 'write_to_hardware') as write:
            bridge.request_transition('B')
            bridge.request_transition('Y')
            bridge.settle_transition()
            write.assert_not_called()

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
            self.assertEqual(list(bridge.active_sessions), ['codex:live'])

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
                self.assertEqual(traffic.parse_input(), ('codex:chat',expected))

class BluetoothTests(unittest.TestCase):
    def test_stalled_write_times_out(self):
        import asyncio
        from ble_transport import BluetoothLink
        class StalledClient:
            is_connected = True
            async def write_gatt_char(self, *args, **kwargs):
                await asyncio.Event().wait()
        link = BluetoothLink('TrafficLight-TEST', lambda:'Y', lambda report:None)
        link.client = StalledClient()
        real_wait = asyncio.wait_for
        async def shortened_wait(awaitable, timeout):
            self.assertEqual(timeout, 5)
            return await real_wait(awaitable, timeout=.01)
        with patch('ble_transport.asyncio.wait_for', shortened_wait):
            with self.assertRaises(asyncio.TimeoutError):
                asyncio.run(link.write(b'Y'))

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
