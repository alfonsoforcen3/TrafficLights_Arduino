import contextlib
import io
import json
import unittest
from unittest.mock import patch, AsyncMock
from types import SimpleNamespace
from scripts import onboard


class OnboardTests(unittest.TestCase):
    def setUp(self):
        # A missed workflow mock must fail immediately, never touch Bluetooth.
        for operation in ('discover_candidates', 'inspect_device', 'identify_device', 'rename_device'):
            guard = patch.object(onboard.device_identity, operation,
                                 new=AsyncMock(side_effect=AssertionError('Unexpected real BLE operation: ' + operation)))
            guard.start()
            self.addCleanup(guard.stop)

    def test_color_requires_capable_tty_and_respects_plain_output(self):
        with patch.dict(onboard.os.environ, {'TERM':'xterm'}, clear=True), \
                patch.object(onboard.os, 'name', 'posix'), \
                patch('sys.stdout.isatty', return_value=True):
            self.assertIn('\x1b[', onboard.WizardUI().paint('Clawdy', '36'))
            self.assertNotIn('\x1b[', onboard.WizardUI(no_color=True).paint('Clawdy', '36'))
            with patch.dict(onboard.os.environ, {'NO_COLOR':''}):
                self.assertNotIn('\x1b[', onboard.WizardUI().paint('Clawdy', '36'))
            with patch.dict(onboard.os.environ, {'TERM':'dumb'}):
                self.assertFalse(onboard.WizardUI().color)
        with patch('sys.stdout.isatty', return_value=False):
            self.assertFalse(onboard.WizardUI().color)
        with patch.dict(onboard.os.environ, {}, clear=True), \
                patch.object(onboard.os, 'name', 'nt'), \
                patch('sys.stdout.isatty', return_value=True):
            self.assertFalse(onboard.WizardUI().color)
            with patch.dict(onboard.os.environ, {'WT_SESSION':'test'}):
                self.assertTrue(onboard.WizardUI().color)

    def test_untrusted_device_names_cannot_inject_terminal_controls(self):
        devices = [{'name':'Toy\x1b[31m\nother', 'address':'A\rB'}]
        with patch('sys.stdin.isatty', return_value=True), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(onboard.select_device(devices, input_fn=lambda _: '1'), devices[0])
        self.assertNotIn('\x1b', output.getvalue())
        self.assertNotIn('\r', output.getvalue())
        self.assertIn(r'\x1b[31m\x0aother', output.getvalue())

    def test_plain_preview_keeps_json_plan_and_explicit_pending_identity(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = onboard.main(['--dry-run','--no-color','--ble-name','Factory',
                                   '--nickname','Pip','--providers','codex'])
        text = output.getvalue()
        self.assertEqual(result,0)
        self.assertNotIn('\x1b',text)
        self.assertIn('C L A W D Y',text)
        self.assertIn('Preview only: no Bluetooth scan, downloads or changes.',text)
        self.assertIn('2/5',text)
        plan = json.loads(text[text.index('{'):])
        self.assertIsNone(plan['installer'])
        self.assertTrue(plan['requested_name'].endswith('<UID8>'))
        self.assertNotIn('Clawdy is linked',text)

    def test_numbered_mocked_setup_never_claims_verification_when_skipped(self):
        identity = self.workflow_identity()
        with patch.object(onboard,'device_identity',identity), \
                patch.object(onboard,'ensure_dependencies',return_value=False), \
                patch.object(onboard,'require_platform',return_value='Darwin'), \
                patch.object(onboard.subprocess,'run'), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            result = onboard.main(['--yes','--no-color','--ble-name','Factory',
                '--nickname','Pip','--no-hooks','--identified-device','--skip-verification'])
        text = output.getvalue()
        self.assertEqual(result,0)
        offsets = [text.index(str(i)+'/5') for i in range(1,6)]
        self.assertEqual(offsets, sorted(offsets))
        self.assertIn('[PENDING]',text)
        self.assertIn('remain unverified',text)
        self.assertNotIn('Clawdy is linked',text)

    def test_name_preview_includes_unknown_identity_suffix(self):
        self.assertEqual(onboard.make_name('My-Mac', 'Clody'), 'My-Mac-Clody-<UID8>')

    def test_preview_uses_final_normalization_and_shortening_policy(self):
        for laptop, nickname in [('é' * 40, 'Clody'), ('mac', 'x' * 22),
                                  ('My Laptop', '  ｃｌｏｄｙ\n toy  '), (' ', '\n')]:
            final = onboard.device_identity.make_device_name(laptop, nickname, '0123456789abcdef')
            preview = onboard.make_name(laptop, nickname)
            self.assertEqual(preview, final[:-8] + '<UID8>')
            self.assertLessEqual(len(final.encode()), 29)

    def test_duplicate_name_needs_address_noninteractive(self):
        devices = [{'name': 'Clody', 'address': 'A'}, {'name': 'Clody', 'address': 'B'}]
        with patch('sys.stdin.isatty', return_value=False):
            with self.assertRaises(RuntimeError):
                onboard.select_device(devices, 'Clody')
            self.assertEqual(onboard.select_device(devices, 'Clody', 'B'), devices[1])
            with self.assertRaises(RuntimeError):
                onboard.select_device(devices)

    def test_interactive_selection_never_auto_chooses(self):
        devices = [{'name': 'Clody', 'address': 'A'}]
        with patch('sys.stdin.isatty', return_value=True):
            self.assertEqual(onboard.select_device(devices, input_fn=lambda _: '1'), devices[0])
            with self.assertRaises(RuntimeError):
                onboard.select_device(devices, input_fn=lambda _: '0')

    def test_dry_run_never_connects_installs_or_checks_dependency(self):
        with patch.object(onboard, 'ensure_dependencies') as deps, patch.object(onboard.subprocess, 'run') as run:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(onboard.main(['--dry-run', '--ble-name', 'TrafficLight-ABCD', '--nickname', 'Clody', '--providers', 'codex']), 0)
            deps.assert_not_called()
            run.assert_not_called()
            self.assertIn('rename_requires_firmware_support', output.getvalue())
            plan = json.loads(output.getvalue()[output.getvalue().index('{'):])
            self.assertTrue(plan['requested_name'].endswith('-<UID8>'))
            self.assertIsNone(plan['installer'])

    def test_live_bootstrap_precedes_interactive_choices(self):
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies', return_value=True) as deps, \
                patch.object(onboard, 'choose_providers') as choose, \
                patch('builtins.input') as prompt, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(onboard.main([]), 0)
        deps.assert_called_once()
        self.assertEqual(deps.call_args.args[1], [])
        choose.assert_not_called()
        prompt.assert_not_called()

    def test_explicit_provider_preflight_precedes_bootstrap(self):
        order = []
        argv = ['--yes', '--ble-name', 'Factory', '--nickname', 'Clody', '--providers', 'gemini']
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard.provider_setup, 'preflight', side_effect=lambda p: order.append(('preflight', p))), \
                patch.object(onboard, 'ensure_dependencies', side_effect=lambda a, v: order.append(('bootstrap', v)) or True), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(onboard.main(argv), 0)
        self.assertEqual(order, [('preflight', ['gemini']), ('bootstrap', argv)])

    def test_keep_name_offline(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            onboard.main(['--dry-run', '--ble-name', 'first clawdy', '--keep-name', '--no-hooks'])
        self.assertIn('first clawdy', output.getvalue())
        self.assertIn('--no-hooks', output.getvalue())

    def test_noninteractive_explicit_requirements(self):
        for flags in (['--yes'], ['--dry-run', '--ble-name', 'abc'], ['--yes', '--nickname', 'x']):
            with self.assertRaises(ValueError):
                onboard.main(flags)

    def test_conflicting_options(self):
        with self.assertRaises(ValueError):
            onboard.main(['--keep-name', '--nickname', 'x'])
        with self.assertRaises(ValueError):
            onboard.main(['--providers', 'codex', '--no-hooks'])

    def test_bridge_only_does_not_autodetect_hooks(self):
        args = onboard.parser().parse_args(['--no-hooks'])
        with patch.object(onboard.provider_setup, 'detect') as detect:
            self.assertEqual(onboard.choose_providers(args), [])
            detect.assert_not_called()

    def test_installer_subprocess_uses_argument_list(self):
        cmd = onboard.installer_command('Mac-$(touch hacked)', ['codex', 'claude'])
        self.assertIn('Mac-$(touch hacked)', cmd)
        self.assertEqual(cmd[-3:], ['--providers', 'codex', 'claude'])

    def workflow_identity(self, rename_supported=True):
        return SimpleNamespace(
            discover_candidates=AsyncMock(return_value=[{'name': 'Factory', 'address': 'A'}]),
            identify_device=AsyncMock(return_value={}),
            inspect_device=AsyncMock(return_value={'ble_name': 'Factory', 'device_id': '0123456789abcdef',
                'identity_protocol': 1, 'rename_supported': rename_supported}),
            make_device_name=lambda *args: 'Mac-Clody-89abcdef',
            rename_device=AsyncMock(return_value={'ok': True, 'persistent': True, 'ble_name': 'Mac-Clody-89abcdef'}))

    def test_verified_rename_precedes_installer(self):
        identity = self.workflow_identity()
        with patch.object(onboard, 'device_identity', identity), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()):
            onboard.main(['--yes', '--ble-name', 'Factory', '--nickname', 'Clody', '--no-hooks', '--identified-device', '--skip-verification'])
        identity.inspect_device.assert_awaited_once_with('A')
        identity.rename_device.assert_awaited_once()
        self.assertIn('Mac-Clody-89abcdef', run.call_args.args[0])

    def test_old_firmware_does_not_install_with_unapplied_name(self):
        identity = self.workflow_identity(False)
        with patch.object(onboard, 'device_identity', identity), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, '--keep-name'):
                onboard.main(['--yes', '--ble-name', 'Factory', '--nickname', 'Clody', '--no-hooks', '--identified-device', '--skip-verification'])
        run.assert_not_called()
        identity.rename_device.assert_not_awaited()

    def test_unacknowledged_rename_stops_install(self):
        identity = self.workflow_identity()
        identity.rename_device.return_value = {'ok': True, 'persistent': False, 'ble_name': 'Mac-Clody-89abcdef'}
        with patch.object(onboard, 'device_identity', identity), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'persistent rename'):
                onboard.main(['--yes', '--ble-name', 'Factory', '--nickname', 'Clody', '--no-hooks', '--identified-device', '--skip-verification'])
        run.assert_not_called()

    def test_provider_preflight_failure_prevents_dependency_or_bluetooth(self):
        with patch.object(onboard.provider_setup, 'preflight', side_effect=RuntimeError('policy disabled')), \
                patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies') as deps, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'policy disabled'):
                onboard.main(['--yes', '--ble-name', 'Factory', '--keep-name', '--providers', 'gemini'])
        deps.assert_not_called()

    def test_yes_does_not_assert_physical_observation(self):
        with patch('sys.stdin.isatty', return_value=False):
            self.assertFalse(onboard.human_confirmation('Did lights show?'))

    def test_missing_physical_identification_stops_before_rename(self):
        identity = self.workflow_identity()
        with patch.object(onboard, 'device_identity', identity), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch('sys.stdin.isatty', return_value=False), \
                patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'Physical selection'):
                onboard.main(['--yes', '--ble-name', 'Factory', '--nickname', 'Clody', '--no-hooks'])
        run.assert_not_called()
        identity.rename_device.assert_not_awaited()

    def test_verification_requires_ble_peer_report_and_visible_confirmation(self):
        from scripts import verify_hardware
        good = {'hardware_connected': True, 'transport': 'ble', 'port': 'ble://A',
                'firmware_report': {'transport': 'ble', 'device_id': 'abc'}}
        with patch.object(verify_hardware, 'request', return_value=good), \
                patch.object(verify_hardware, 'verify') as verify, \
                patch.object(onboard, 'human_confirmation', return_value=False), \
                patch('sys.stdin.isatty', return_value=False), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(onboard.verify_install('abc'))
        verify.assert_called_once_with('ble')

    def test_wrong_peer_identity_is_not_verified(self):
        from scripts import verify_hardware
        wrong = {'hardware_connected': True, 'transport': 'ble', 'port': 'ble://A',
                 'firmware_report': {'transport': 'ble', 'device_id': 'other'}}
        with patch.object(verify_hardware, 'request', return_value=wrong), \
                patch.object(verify_hardware, 'verify') as verify, \
                patch('sys.stdin.isatty', return_value=False), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'not verified'):
                onboard.verify_install('abc', timeout=0)
        verify.assert_not_called()

    def test_denied_visible_identification_never_renames_or_installs(self):
        identity = self.workflow_identity()
        with patch.object(onboard, 'device_identity', identity), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'human_confirmation', return_value=False), \
                patch('sys.stdin.isatty', return_value=True), \
                patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'not physically confirmed'):
                onboard.main(['--yes', '--ble-name', 'Factory', '--nickname', 'Clody', '--no-hooks'])
        identity.identify_device.assert_awaited_once()
        identity.rename_device.assert_not_awaited()
        run.assert_not_called()

    def test_verified_and_visible_leds_finish_hardware_only(self):
        from scripts import verify_hardware
        good = {'hardware_connected': True, 'transport': 'ble', 'port': 'ble://A',
                'firmware_report': {'transport': 'ble', 'device_id': 'abc'}}
        with patch.object(verify_hardware, 'request', return_value=good), \
                patch.object(verify_hardware, 'verify'), \
                patch.object(onboard, 'human_confirmation', return_value=True), \
                patch('sys.stdin.isatty', return_value=False), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertTrue(onboard.verify_install('abc'))
        self.assertIn('Real-provider acceptance', output.getvalue())


if __name__ == '__main__':
    unittest.main()
