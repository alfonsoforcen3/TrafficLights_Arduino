import contextlib
import io
import json
import os
import plistlib
import re
from pathlib import Path
import subprocess
import tempfile
import sys
from types import SimpleNamespace
import unittest
import zipfile
from unittest.mock import AsyncMock, patch

import install
from scripts import onboard, provider_setup, build_customer_bundle


class CustomerIntentTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.runtime = self.root/'runtime'
        for module in (install, onboard):
            guard = patch.object(module, 'RUNTIME', self.runtime)
            guard.start(); self.addCleanup(guard.stop)
        # Every unexpected hardware operation must fail before reaching Bleak.
        for name in ('discover_candidates', 'inspect_device', 'identify_device', 'rename_device'):
            guard = patch.object(onboard.device_identity, name,
                                 new=AsyncMock(side_effect=AssertionError('Unexpected BLE: ' + name)))
            guard.start(); self.addCleanup(guard.stop)
        for name in ('usb_inventory', 'inspect_usb_device'):
            guard = patch.object(onboard.device_identity, name, side_effect=AssertionError('Unexpected USB: ' + name))
            guard.start(); self.addCleanup(guard.stop)

    def test_fresh_no_arguments_enters_guided_bluetooth_not_usb(self):
        with patch('sys.argv', ['install.py']), patch.object(onboard, 'run_cli', return_value=2) as wizard, \
                patch.object(install.subprocess, 'run') as run:
            self.assertEqual(install.main(), 2)
        wizard.assert_called_once_with([]); run.assert_not_called()

    def test_saved_connection_and_explicit_maintenance_keep_their_paths(self):
        self.runtime.mkdir()
        path = self.runtime/'connection.json'
        for transport in ('ble', 'serial'):
            path.write_text(json.dumps({'transport': transport, 'ble_name': 'Exact toy'}))
            before = path.read_bytes()
            self.assertTrue(install.onboarding_requested([]))
            self.assertEqual(path.read_bytes(), before)
        for argv in (['--help'], ['--no-hooks'], ['--ble-name', 'Exact toy'], ['--transport', 'serial']):
            self.assertFalse(install.onboarding_requested(argv))

    def test_invalid_saved_connection_never_silently_scans_another_unit(self):
        self.runtime.mkdir(); path = self.runtime/'connection.json'
        for content in ('{bad', '[]', '{"transport":"ble"}', '{"transport":"other"}'):
            path.write_text(content)
            with self.assertRaisesRegex(RuntimeError, 'needs recovery'):
                install.onboarding_requested([])
            self.assertEqual(path.read_text(), content)

    def test_serial_maintenance_requires_explicit_transport_and_never_discovers_usb(self):
        self.runtime.mkdir(); (self.runtime/'connection.json').write_text('{"transport":"serial","ble_name":null}')
        from scripts import codex_setup, platform_support
        with patch('sys.argv', ['install.py', '--no-hooks']), patch.object(install.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'explicitly request --transport serial'):
                install.main()
        run.assert_not_called()
        with patch('sys.argv', ['install.py', '--no-hooks', '--transport', 'serial']), patch.object(install.sys, 'prefix', str(self.runtime/'venv')), \
                patch.object(platform_support, 'require_platform', return_value='Darwin'), \
                patch.object(provider_setup, 'detect', return_value={}), patch.object(codex_setup, 'install_service') as service, \
                contextlib.redirect_stdout(io.StringIO()):
            install.main()
        service.assert_called_once_with('serial', None, device_id=None)

    def test_buyer_installer_is_explicit_ble_even_with_saved_serial_profile(self):
        self.runtime.mkdir(); (self.runtime/'connection.json').write_text('{"transport":"serial"}')
        from scripts import codex_setup, platform_support
        command = onboard.installer_command('Selected toy', [], '0123456789ABCDEF')
        with patch('sys.argv', command[1:]), patch.object(install.sys, 'prefix', str(self.runtime/'venv')), \
                patch.object(platform_support, 'require_platform', return_value='Darwin'), \
                patch.object(codex_setup, 'install_service') as service, contextlib.redirect_stdout(io.StringIO()):
            install.main()
        service.assert_called_once_with('ble', 'Selected toy', device_id='0123456789ABCDEF')

    def test_noninteractive_provider_choice_is_required_before_dependencies(self):
        with patch.object(onboard, 'ensure_dependencies') as deps:
            with self.assertRaisesRegex(ValueError, 'explicit --providers or --no-hooks'):
                onboard.main(['--yes', '--ble-name', 'Selected', '--keep-name'])
        deps.assert_not_called()

    def test_existing_profile_requires_replacement_confirmation_before_dependencies(self):
        self.runtime.mkdir(); path = self.runtime/'connection.json'
        path.write_text('{"transport":"ble","ble_name":"Previous toy","device_id":"01234567"}')
        before = path.read_bytes()
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies') as deps, contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(RuntimeError, '--replace-existing'):
                onboard.main(['--yes', '--ble-name', 'Next toy', '--keep-name', '--no-hooks'])
        self.assertIn('Previous toy', output.getvalue()); self.assertIn('01234567', output.getvalue())
        deps.assert_not_called(); self.assertEqual(path.read_bytes(), before)

    def test_existing_profile_change_after_confirmation_stops_before_any_mutation(self):
        args = onboard.parser().parse_args(['--yes', '--ble-name', 'Selected', '--keep-name', '--no-hooks'])
        args.existing_connection = None
        self.runtime.mkdir(); (self.runtime/'connection.json').write_text('{"transport":"ble","ble_name":"Changed"}')
        with patch.object(onboard.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'changed during setup'):
                onboard.complete_setup(args, onboard.WizardUI(), {'address': 'A'}, {'ble_name': 'Selected'}, [], None)
        run.assert_not_called(); self.assertFalse((self.runtime/'onboarding').exists())

    def test_usb_metadata_is_opt_in_and_never_bootstraps_or_opens_ports(self):
        metadata = {'available': True, 'ports': [{'port': 'MOCK', 'board_model_verified': False}], 'reason': None}
        with patch.object(onboard.device_identity, 'usb_inventory', return_value=metadata), \
                patch.object(onboard, 'ensure_dependencies') as deps, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(onboard.main(['--list-usb', '--json']), 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload['mode'], 'usb_inventory'); self.assertFalse(payload['ports_opened'])
        self.assertFalse(payload['bluetooth_scanned']); self.assertFalse(payload['mutations'])
        self.assertEqual(payload['runtime_transport'], 'ble'); deps.assert_not_called()

    def test_usb_ble_mismatch_stops_before_identification_rename_or_install(self):
        usb = {'device_id': 'AABBCCDDEEFF', 'hardware_family': 'esp32c3', 'ble_name': 'Selected'}
        ble = dict(usb, device_id='112233445566')
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard.device_identity, 'discover_candidates', new=AsyncMock(return_value=[{'name': 'Selected', 'address': 'A'}])), \
                patch.object(onboard.device_identity, 'inspect_usb_device', return_value=usb), \
                patch.object(onboard.device_identity, 'inspect_device', new=AsyncMock(return_value=ble)), \
                patch.object(onboard.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'USB and BLE identities/names do not match'):
                onboard.main(['--yes', '--ble-name', 'Selected', '--keep-name', '--no-hooks',
                              '--usb-port', 'MOCK', '--usb-serial', 'MOCK-SERIAL', '--identified-device'])
        onboard.device_identity.identify_device.assert_not_awaited()
        onboard.device_identity.rename_device.assert_not_awaited(); run.assert_not_called()

    def test_preflight_json_is_offline_and_preserves_disabled_provider_policy(self):
        with patch.object(provider_setup, 'detect', return_value={'codex': ['fixture/codex']}), \
                patch.object(provider_setup, 'preflight', side_effect=RuntimeError('Hooks are disabled')), \
                patch.object(onboard.importlib.util, 'find_spec', return_value=None), \
                patch.object(onboard, 'ensure_dependencies') as deps, patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(onboard.main(['--preflight', '--json']), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report['mode'], 'preflight')
        self.assertFalse(report['mutations']); self.assertFalse(report['bluetooth_scanned'])
        self.assertFalse(report['customer_ready'])
        self.assertEqual(report['providers']['codex']['hook_policy'], 'blocked')
        self.assertFalse(report['providers']['codex']['selected'])
        self.assertTrue(report['provider_selection_required'])
        self.assertEqual(report['runtime_transport'], 'ble')
        deps.assert_not_called(); run.assert_not_called(); self.assertFalse(self.runtime.exists())

    def test_provider_inventory_never_treats_detection_as_hook_consent(self):
        with patch('sys.argv', ['provider_setup.py', '--detect', '--json']), \
                patch.object(provider_setup, 'detect', return_value={'codex': ['mock executable']}), \
                patch.object(provider_setup, 'configure') as configure, contextlib.redirect_stdout(io.StringIO()) as output:
            provider_setup.main()
        report = json.loads(output.getvalue())
        self.assertIn('codex', report['detected']); self.assertFalse(report['mutations'])
        self.assertIn('Claude Desktop chats', report['unsupported']); configure.assert_not_called()
        with patch('sys.argv', ['provider_setup.py']), patch.object(provider_setup, 'detect', return_value={'codex': ['mock']}), \
                patch.object(provider_setup, 'configure') as configure, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                provider_setup.main()
        configure.assert_not_called()

    def test_discovery_json_does_not_connect_identify_rename_or_install(self):
        devices = [{'name': 'Clawdy One', 'address': 'MOCK-A', 'rssi': -40},
                   {'name': 'Clawdy Two', 'address': 'MOCK-B', 'rssi': -50}]
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard.device_identity, 'discover_candidates', new=AsyncMock(return_value=devices)), \
                patch.object(onboard, 'choose_providers') as choose, patch.object(onboard.subprocess, 'run') as run, \
                contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(onboard.main(['--list-devices', '--json', '--yes']), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report['devices'], devices)
        self.assertTrue(report['explicit_selection_required']); self.assertFalse(report['firmware_verified'])
        self.assertFalse(report['customer_ready']); choose.assert_not_called(); run.assert_not_called()
        onboard.device_identity.inspect_device.assert_not_awaited()
        onboard.device_identity.identify_device.assert_not_awaited()
        onboard.device_identity.rename_device.assert_not_awaited()

    def test_discovery_cannot_silently_accept_setup_flags(self):
        with patch.object(onboard, 'ensure_dependencies') as deps:
            for extra in (['--nickname', 'Pip'], ['--providers', 'codex'], ['--identified-device']):
                with self.assertRaisesRegex(ValueError, 'only lists'):
                    onboard.main(['--list-devices', '--yes', *extra])
            deps.assert_not_called()

    def test_json_selection_is_explicit_and_never_prompts_for_ambiguous_name(self):
        devices = [{'name': 'Factory', 'address': 'A'}, {'name': 'Factory', 'address': 'B'}]
        with patch('sys.stdin.isatty', return_value=True):
            with self.assertRaises(RuntimeError):
                onboard.select_device(devices, 'Factory', allow_prompt=False)
            self.assertEqual(onboard.select_device(devices, address='B', allow_prompt=False), devices[1])

    def test_machine_readable_install_keeps_physical_and_provider_checks_pending(self):
        report = {'firmware': 'traffic-nicenano-v1', 'ble_name': 'Factory', 'device_id': '0123456789abcdef'}
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies', return_value=False), \
                patch.object(onboard.device_identity, 'discover_candidates', new=AsyncMock(return_value=[{'name': 'Factory', 'address': 'A'}])), \
                patch.object(onboard.device_identity, 'inspect_device', new=AsyncMock(return_value=report)), \
                patch.object(onboard.device_identity, 'identify_device', new=AsyncMock(return_value=report)), \
                patch.object(onboard.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()) as output, \
                contextlib.redirect_stderr(io.StringIO()):
            result = onboard.main(['--yes', '--json', '--device-address', 'A', '--keep-name', '--no-hooks',
                                   '--identified-device', '--skip-verification'])
        self.assertEqual(result, 0)
        summary = json.loads(output.getvalue())
        self.assertEqual(summary['phase'], 'installed_unverified')
        self.assertTrue(summary['software_installed']); self.assertFalse(summary['customer_ready'])
        self.assertEqual(summary['physical_selection'], 'operator_asserted')
        self.assertEqual(summary['verification']['visible_leds'], 'pending')
        self.assertEqual(summary['verification']['provider_trust'], 'pending')
        self.assertIn('--ble-name', run.call_args.args[0]); self.assertIn('Factory', run.call_args.args[0])
        checkpoint = json.loads(Path(summary['recovery_record']).read_text())
        self.assertFalse(checkpoint['customer_ready'])

    def test_verification_distinguishes_gpio_ack_from_visible_led_confirmation(self):
        from scripts import verify_hardware
        good = {'hardware_connected': True, 'transport': 'ble', 'port': 'ble://MOCK',
                'firmware_report': {'transport': 'ble', 'device_id': '01234567', 'ble_name': 'Factory'}}
        checks = {'bluetooth_delivery': 'pending', 'gpio_acknowledgements': 'pending', 'visible_leds': 'pending'}
        with patch.object(verify_hardware, 'request', return_value=good), patch.object(verify_hardware, 'verify'), \
                patch.object(onboard, 'human_confirmation', return_value=False), patch('sys.stdin.isatty', return_value=False), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(onboard.verify_install('01234567', expected_name='Factory', checks=checks))
        self.assertEqual(checks, {'bluetooth_delivery': 'passed', 'gpio_acknowledgements': 'passed', 'visible_leds': 'pending'})

    def test_verification_rejects_different_legacy_name_without_immutable_identity(self):
        from scripts import verify_hardware
        status = {'hardware_connected': True, 'transport': 'ble', 'port': 'ble://MOCK',
                  'firmware_report': {'transport': 'ble', 'ble_name': 'Other toy'}}
        with patch.object(verify_hardware, 'request', return_value=status), patch.object(verify_hardware, 'verify') as verify, \
                patch('sys.stdin.isatty', return_value=False), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'name differs'):
                onboard.verify_install(expected_name='Factory', timeout=0)
        verify.assert_not_called()

    def test_dependency_relaunch_propagates_pending_child_exit(self):
        args = onboard.parser().parse_args(['--yes'])
        with patch.object(onboard.importlib.util, 'find_spec', return_value=None), \
                patch.object(Path, 'exists', return_value=True), patch.object(onboard.subprocess, 'run', side_effect=[
                    subprocess.CompletedProcess(['pip'], 0), subprocess.CompletedProcess(['wizard'], 2)]), \
                contextlib.redirect_stdout(io.StringIO()):
            result = onboard.ensure_dependencies(args, ['--yes'])
        self.assertEqual(result.returncode, 2)
        with patch.object(onboard, 'require_platform', return_value='Darwin'), \
                patch.object(onboard, 'ensure_dependencies', return_value=result), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(onboard.main([]), 2)

    def test_detection_requires_hook_capable_app_identity_not_desktop_brand(self):
        apps = self.root/'Applications'
        def app(name, identifier):
            path = apps/name/'Contents'; path.mkdir(parents=True, exist_ok=True)
            (path/'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': identifier}))
        app('ChatGPT.app', 'com.openai.chat'); app('Claude.app', 'com.anthropic.claudefordesktop')
        with patch.object(Path, 'home', return_value=self.root), patch.object(provider_setup.shutil, 'which', return_value=None):
            found = provider_setup.detect([apps])
            self.assertNotIn('codex', found); self.assertNotIn('claude', found)
            app('Codex.app', 'com.openai.codex')
            self.assertIn('codex', provider_setup.detect([apps]))
            (apps/'Codex.app/Contents/Info.plist').write_bytes(b'<?xml version="1.0"?><plist><dict><key>unfinished')
            self.assertNotIn('codex', provider_setup.detect([apps]))

    def populate_bundle(self):
        for name in build_customer_bundle.FILES + tuple(build_customer_bundle.DOCUMENTS.values()):
            path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text('fixture\n')

    def test_bundle_rejects_unsafe_guides_before_creating_archive(self):
        self.populate_bundle()
        guide = self.root/'docs/CUSTOMER_AGENT.md'; guide.unlink()
        try:
            guide.symlink_to(self.root/'install.py')
        except OSError:
            self.skipTest('Creating a symlink is not permitted on this test machine')
        output = self.root/'candidate.zip'
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            build_customer_bundle.build(output, self.root)
        self.assertFalse(output.exists())

    def test_bundle_output_cannot_overwrite_allowlisted_source(self):
        self.populate_bundle(); path = self.root/'install.py'; before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            build_customer_bundle.build(path, self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_extracted_bundle_runs_offline_agent_commands_and_has_working_local_links(self):
        archive = self.root/'customer.zip'
        build_customer_bundle.build(archive)
        extracted = self.root/'extracted'
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(extracted)  # Only our generated explicit allowlist.
        checkout = extracted/'Clawdy'
        before = {str(path.relative_to(checkout)): path.read_bytes() for path in checkout.rglob('*') if path.is_file()}
        home = self.root/'isolated-home'; home.mkdir()
        environment = dict(os.environ, HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home/'.codex'))
        environment.pop('PYTHONDONTWRITEBYTECODE', None)
        # Apple's CLT interpreter writes its own site/encoding caches before
        # program entry, even for `python -c pass`. Separate that startup effect
        # from mutations caused by the onboarding command itself.
        subprocess.run([sys.executable, '-c', 'pass'], env=environment, check=True, timeout=15)
        home_before = {str(path.relative_to(home)): path.read_bytes() for path in home.rglob('*') if path.is_file()}
        for arguments in (['--preflight', '--json'],
                          ['--dry-run', '--json', '--ble-name', 'Factory', '--keep-name', '--no-hooks']):
            result = subprocess.run([sys.executable, str(checkout/'install.py'), '--onboard', *arguments],
                                    cwd=checkout, env=environment, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload.get('customer_ready', False))
        after = {str(path.relative_to(checkout)): path.read_bytes() for path in checkout.rglob('*') if path.is_file()}
        self.assertEqual(before, after, 'Offline commands must not create bytecode or modify the extracted bundle')
        home_after = {str(path.relative_to(home)): path.read_bytes() for path in home.rglob('*') if path.is_file()}
        self.assertEqual(home_before, home_after, 'Offline commands must not create a user runtime or hook settings')
        for document in checkout.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                target = target.strip('<>').split('#', 1)[0]
                if not target or re.match(r'^[a-zA-Z]+:', target):
                    continue
                self.assertTrue((document.parent/target).exists(), str(document.relative_to(checkout)) + ': ' + target)


if __name__ == '__main__':
    unittest.main()
