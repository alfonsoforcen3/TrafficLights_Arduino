import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from scripts import flash_nicenano, platform_support, provider_setup


class FirmwareUpdateTests(unittest.TestCase):
    def test_pwm_boolean_contract_and_invalid_ratios(self):
        class PWM:
            def __init__(self, pin, frequency, duty_cycle):
                self.frequency, self.duty_cycle = frequency, duty_cycle
        source = Path(__file__).resolve().parents[1] / 'firmware/nicenano/pwm_led.py'
        spec = importlib.util.spec_from_file_location('tested_pwm', source)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'pwmio': SimpleNamespace(PWMOut=PWM)}):
            spec.loader.exec_module(module)
        led = module.PwmLED('P0.09')
        self.assertEqual(led._pwm.frequency, 5000)
        self.assertEqual(led._pwm.duty_cycle, 0)
        led.value = True
        self.assertTrue(led.value)
        self.assertEqual(led._pwm.duty_cycle, 32768)
        led.value = False
        self.assertEqual(led._pwm.duty_cycle, 0)
        for value in (-.1, 1.1, float('nan'), float('inf'), 'bad'):
            with self.assertRaises(ValueError):
                module.PwmLED('pin', value)

    def test_auto_discovery_refuses_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            roots = [Path(directory)/name for name in ('A', 'B')]
            for root in roots:
                root.mkdir(); (root/'boot_out.txt').write_text('nice!nano')
            with patch.object(flash_nicenano.sys, 'platform', 'darwin'), \
                 patch.object(Path, 'iterdir', return_value=iter(roots)):
                with self.assertRaises(RuntimeError):
                    flash_nicenano.auto_detect_circuitpy()

    def test_existing_profile_is_preserved_and_dependency_precedes_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); drive = root/'board'; drive.mkdir()
            (drive/'boot_out.txt').write_text('CircuitPython 8.1.0; nice!nano')
            profile = '{"green_pin":"P0.09","ble_name":"first clawdy"}'
            (drive/'hardware_config.json').write_text(profile)
            with patch.object(flash_nicenano, 'ROOT', root), \
                 patch.object(flash_nicenano.shutil, 'copyfile') as copy:
                flash_nicenano.provision(None, drive)
                sources = [str(call.args[0]) for call in copy.call_args_list]
                self.assertLess(next(i for i,s in enumerate(sources) if s.endswith('/pwm_led.py')),
                                next(i for i,s in enumerate(sources) if s.endswith('/code.py')))
            self.assertEqual((drive/'hardware_config.json').read_text(), profile)

    def test_powershell_literal_paths_and_legacy_hook_ownership(self):
        with patch.object(platform_support.platform, 'system', return_value='Windows'):
            command = platform_support.hook_command("C:/O'Brien/$toy/python.exe", 'C:/toy/traffic.py', powershell=True)
            self.assertTrue(command.startswith("& '"))
            self.assertIn("O''Brien/$toy", command)
        unrelated = {'name':'traffic-light-other', 'command':'other-tool'}
        legacy = {'name':'traffic-light-old', 'command':'python traffic.py Y --provider gemini'}
        data = {'hooks':{'BeforeModel':[{'hooks':[unrelated, legacy]}]}}
        provider_setup.remove_ours(data, 'gemini')
        self.assertEqual(data['hooks']['BeforeModel'][0]['hooks'], [unrelated])
        self.assertNotIn('BeforeModel', provider_setup.EVENTS['gemini'])
        self.assertEqual(provider_setup.EVENTS['gemini']['AfterTool'], 'Y')
        self.assertEqual(provider_setup.EVENTS['gemini']['AfterAgent'], 'G')
