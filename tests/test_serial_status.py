"""Execute the real USB watchdog function with mocked ports and a one-loop stop."""
import ast
import contextlib
import io
import json
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from scripts.dashboard import firmware_status


class StopLoop(BaseException):
    pass


class SerialStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / 'scripts/bridge.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'hardware_watchdog')
        cls.code = compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec')

    def one_cycle(self, data=b'', *, alive=True, error=False):
        class Port:
            port = 'fixture-only'
            closed = False
            def read(self, _limit):
                if error: raise OSError('fixture disconnect')
                return data
            def close(self): self.closed = True
            def write(self, _data): raise AssertionError('No heartbeat due in this fixture')
            def flush(self): pass
        port = Port(); reports = []
        def stop(_seconds): raise StopLoop()
        def no_open(*_args, **_kwargs): raise AssertionError('Real serial opening forbidden')
        state = dict(ser_conn=port, ser_lock=threading.Lock(), hardware_synced=True,
                     firmware_report={'firmware': 'old'}, current_hardware_state='Y',
                     BAUD_RATE=115200, find_serial_port=lambda: None,
                     firmware_status=firmware_status, json=json,
                     time=SimpleNamespace(time=lambda: 100, sleep=stop),
                     os=SimpleNamespace(name='posix', path=SimpleNamespace(exists=lambda _: alive)),
                     serial=SimpleNamespace(Serial=no_open))
        exec(self.code, state)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(StopLoop):
            state['hardware_watchdog'](reports.append)
        return port, state, reports

    def test_usb_gpio_report_updates_status_without_probing_another_port(self):
        for family in ('traffic-nicenano-v1', 'traffic-esp32c3-v1'):
            raw = {'firmware': family, 'mode': 'Y', 'transport': 'usb', 'private_prompt': 'PRIVATE'}
            port, state, reports = self.one_cycle((json.dumps(raw) + '\n').encode())
            self.assertFalse(port.closed)
            self.assertEqual(len(reports), 1)
            self.assertEqual(reports[0]['mode'], 'Y')
            self.assertEqual(reports[0]['transport'], 'usb')
            self.assertNotIn('PRIVATE', json.dumps(state['firmware_report']))

    def test_unplug_and_read_error_clear_the_dashboard_report(self):
        for options in ({'alive': False}, {'error': True}):
            port, state, reports = self.one_cycle(**options)
            self.assertTrue(port.closed)
            self.assertIsNone(state['ser_conn'])
            self.assertIsNone(state['firmware_report'])
            self.assertEqual(reports, [None])
