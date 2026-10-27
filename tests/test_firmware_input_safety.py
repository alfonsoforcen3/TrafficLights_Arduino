"""Execute actual nRF command decoding/dispatch AST with mocked hardware globals.

No CircuitPython import, USB device, Bluetooth connection or infinite loop runs.
"""
import ast
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

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
        state = dict(commands=data, transport=transport, mode='O',
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

    def test_unsupported_legacy_query_does_not_change_outputs_or_emit_a_report(self):
        for transport in ('ble', 'usb'):
            state, lights, reports, resets = self.run_input(b'Vv', transport)
            self.assertEqual(state['mode'], 'O')
            self.assertEqual((lights, reports, resets), ([], [], []))

    def test_usb_initialization_and_report_preserve_gpio_profile_without_sensor_imports(self):
        tree = ast.parse(SOURCE.read_text())
        startup = ast.Module(body=[node for node in tree.body if not isinstance(node, ast.While)], type_ignores=[])
        writes, pins = [], []
        class LED:
            value = False
            def __init__(self, pin): pins.append(pin)
            def switch_to_output(self, value): self.value = value
        class PWM(LED):
            def __init__(self, pin, ratio): super().__init__(pin); self.max_duty = 32768
        port = types.SimpleNamespace(connected=True, write=writes.append)
        link = types.SimpleNamespace(connected=False, name='fixture', device_id='FIXTURE', rename_supported=True)
        replacements = {
            'digitalio': types.SimpleNamespace(DigitalInOut=LED),
            'microcontroller': types.SimpleNamespace(pin=types.SimpleNamespace(P0_09='P0.09', P1_11='P1.11', P1_13='P1.13')),
            'usb_cdc': types.SimpleNamespace(data=port),
            'connection_display': types.SimpleNamespace(ConnectionDisplay=lambda: object()),
            'pwm_led': types.SimpleNamespace(PwmLED=PWM),
            'session_count': types.SimpleNamespace(SessionCount=lambda: object()),
            'ble_link': types.SimpleNamespace(Link=lambda: link)}
        original_import = __import__
        def guarded_import(name, *args, **kwargs):
            if name == 'analogio': raise AssertionError('No ADC initialization in USB product firmware')
            return original_import(name, *args, **kwargs)
        def profile(path, *args, **kwargs):
            self.assertEqual(path, '/hardware_config.json')
            return io.StringIO('{"green_pin":"P0.09","ble_name":"fixture"}')
        namespace = {}
        with patch.dict(sys.modules, replacements), patch('builtins.open', side_effect=profile), \
                patch('builtins.__import__', side_effect=guarded_import):
            exec(compile(startup, str(SOURCE), 'exec'), namespace)
            namespace['report']('usb')
        self.assertEqual(pins, ['P0.09', 'P1.11', 'P1.13'])
        payload = json.loads(writes[-1])
        self.assertEqual(payload['transport'], 'usb')
        self.assertEqual(payload['green_pwm_duty'], 32768)
        self.assertEqual(set(payload), {'firmware','hardware_family','mode','display_phase','green_pwm_duty',
            'green_pwm_frequency','green_pin','amber_pin','red_pin','P0.09','P1.11','P1.13','oled_error',
            'transport','session_count','session_count_kind','working_provider_mask','ble_name','device_id',
            'identity_protocol','rename_supported','ble_error'})


if __name__ == '__main__':
    unittest.main()
