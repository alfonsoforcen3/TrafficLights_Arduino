"""Compile/run the actual candidate C++ parser; no Arduino runtime or hardware."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'firmware' / 'esp32c3'


class ESP32ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('c++')
        if not cls.compiler:
            raise unittest.SkipTest('Native C++ compiler unavailable; ESP32 parser tests not run')
        cls.temporary = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.temporary.name) / 'protocol_test'
        result = subprocess.run([cls.compiler, '-std=c++11', '-Wall', '-Wextra', '-Werror',
                                 str(SOURCE / 'protocol_test.cpp'), '-o', str(cls.binary)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            cls.temporary.cleanup()
            raise AssertionError(result.stderr)
        cls.runtime_binary = Path(cls.temporary.name) / 'runtime_test'
        result = subprocess.run([cls.compiler, '-std=c++11', '-Wall', '-Wextra', '-Werror',
                                 str(SOURCE / 'runtime_test.cpp'), '-o', str(cls.runtime_binary)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            cls.temporary.cleanup()
            raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def scenario(self, name):
        result = subprocess.run([str(self.binary), name], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_fragmented_rename_never_becomes_colour_commands(self):
        self.scenario('fragmented_identity')

    def test_overflow_discards_payload_until_newline_and_recovers(self):
        self.scenario('identity_bounds')

    def test_session_count_provider_mask_bounds_and_payload_isolation(self):
        self.scenario('metadata')

    def test_disconnect_resets_partial_frames_and_metadata(self):
        self.scenario('disconnect_reset')

    def test_transport_overflow_requires_release_then_accepts_query_without_newline(self):
        self.scenario('transport_overflow')

    def test_legacy_commands_and_lowercase(self):
        self.scenario('legacy')

    def test_name_utf8_byte_limits_controls_and_invalid_encoding(self):
        self.scenario('utf8')

    def test_shipping_runtime_policies_without_radio_or_hardware(self):
        for name in ('usb_diagnostics', 'connect_resume', 'clock_wrap', 'peer_epochs',
                     'transmit_bounds', 'advertisement_ack_drain', 'output_stall_recovery',
                     'persistent_name', 'immutable_identity'):
            with self.subTest(scenario=name):
                result = subprocess.run([str(self.runtime_binary), name], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)

    def config(self, *definitions, source=''):
        return subprocess.run([self.compiler, '-std=c++11', '-x', 'c++', '-fsyntax-only',
                               '-include', str(SOURCE / 'factory_config.h'),
                               *['-D' + value for value in definitions], '-'],
                              input=source, capture_output=True, text=True)

    def test_factory_config_refuses_missing_wiring(self):
        result = self.config()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Factory wiring required', result.stderr)

    def test_factory_config_refuses_duplicate_pins(self):
        result = self.config('CLAWDY_GREEN_GPIO=1', 'CLAWDY_AMBER_GPIO=1',
                             'CLAWDY_RED_GPIO=3', 'CLAWDY_ACTIVE_HIGH=1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('LED pins must be distinct', result.stderr)

    def test_factory_config_requires_polarity(self):
        result = self.config('CLAWDY_GREEN_GPIO=1', 'CLAWDY_AMBER_GPIO=2', 'CLAWDY_RED_GPIO=3')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Factory polarity required', result.stderr)

    def test_mock_factory_config_compiles_without_board_claim(self):
        result = self.config('CLAWDY_GREEN_GPIO=1', 'CLAWDY_AMBER_GPIO=2',
                             'CLAWDY_RED_GPIO=3', 'CLAWDY_ACTIVE_HIGH=1')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pwm_factory_default_and_bounds_are_12_bit(self):
        wiring = ('CLAWDY_GREEN_GPIO=1', 'CLAWDY_AMBER_GPIO=2',
                  'CLAWDY_RED_GPIO=3', 'CLAWDY_ACTIVE_HIGH=1')
        result = self.config(*wiring, source='''
static_assert(CLAWDY_GREEN_DUTY == 2048, "Default half duty changed");
static_assert(CLAWDY_GREEN_PWM_MAX == 4095, "Wrong duty maximum");
static_assert(CLAWDY_GREEN_PWM_BITS == 12, "Wrong resolution");
static_assert(CLAWDY_GREEN_PWM_HZ == 5000, "Wrong frequency");
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        for duty in (0, 4095):
            result = self.config(*wiring, 'CLAWDY_GREEN_DUTY=' + str(duty))
            self.assertEqual(result.returncode, 0, result.stderr)
        for duty in (-1, 4096):
            result = self.config(*wiring, 'CLAWDY_GREEN_DUTY=' + str(duty))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('12-bit duty required', result.stderr)
