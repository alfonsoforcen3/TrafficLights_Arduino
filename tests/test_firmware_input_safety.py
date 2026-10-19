"""Execute actual nRF command decoding/dispatch AST with mocked hardware globals.

No CircuitPython import, USB device, Bluetooth connection or infinite loop runs.
"""
import ast
from pathlib import Path
import types
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'firmware/nicenano/code.py'


class FirmwareInputSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(SOURCE.read_text())
        decoder = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                       and node.name == 'decode_legacy_commands')
        dispatch = next(node for node in ast.walk(tree) if isinstance(node, ast.For)
                        and isinstance(node.target, ast.Name) and node.target.id == 'cmd')
        cls.dispatch = compile(ast.Module(body=[decoder, dispatch], type_ignores=[]),
                               str(SOURCE), 'exec')

    def run_input(self, data, transport='ble'):
        lights, reports, resets = [], [], []
        state = dict(commands=data, transport=transport, mode='O', battery=None,
                     display_phase='tracking', last_blink=0, blink_on=False,
                     time=types.SimpleNamespace(monotonic=lambda: 123, sleep=lambda _: None),
                     microcontroller=types.SimpleNamespace(reset=lambda: resets.append(True)),
                     set_lights=lambda **values: lights.append(values),
                     report=lambda transport: reports.append(transport))
        exec(self.dispatch, state)
        return state, lights, reports, resets

    def test_invalid_bytes_are_rejected_without_dispatch_or_exception(self):
        for transport in ('ble', 'usb'):
            for data in (b'\xff\x80', b'\xf0\x9f\x90\xb1', b'\xc0\xaf', bytes(range(128, 256))):
                with self.subTest(transport=transport, data=data):
                    state, lights, reports, resets = self.run_input(data, transport)
                    self.assertEqual(state['mode'], 'O')
                    self.assertEqual((lights, reports, resets), ([], [], []))

    def test_valid_commands_survive_malformed_bytes_and_lowercase_still_works(self):
        state, lights, reports, resets = self.run_input(b'\xffy\x80q\xfe')
        self.assertEqual(state['mode'], 'Y')
        self.assertEqual(lights, [dict(g=False, y=True, r=False)])
        self.assertEqual(reports, ['ble', 'ble'])
        self.assertEqual(resets, [])

    def test_invalid_bytes_do_not_expose_ble_reset_and_usb_reset_is_preserved(self):
        for transport in ('ble', 'usb'):
            _, _, _, resets = self.run_input(b'\xffx\x80', transport)
            self.assertEqual(resets, [True] if transport == 'usb' else [])


if __name__ == '__main__':
    unittest.main()
