import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import build_customer_bundle, provider_setup
from scripts.ble_transport import BluetoothLink


class CustomerReleaseTests(unittest.TestCase):
    def test_installer_forwards_onboarding_arguments_and_incomplete_status(self):
        import install
        with patch('sys.argv', ['install.py', '--onboard', '--no-hooks']), \
                patch('scripts.onboard.main', return_value=2) as wizard:
            self.assertEqual(install.main(), 2)
            wizard.assert_called_once_with(['--no-hooks'])

    def test_bundle_allowlist_excludes_private_material_and_matches_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in build_customer_bundle.FILES + ('docs/CUSTOMER_SETUP.md', 'docs/CUSTOMER_AGENT.md'):
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('candidate\n')
            (root/'secret.log').write_text('must never ship')
            archive = root/'candidate.zip'
            checksum = build_customer_bundle.build(archive, root)
            self.assertEqual(checksum, hashlib.sha256(archive.read_bytes()).hexdigest())
            with zipfile.ZipFile(archive) as bundle:
                self.assertNotIn('Clawdy/secret.log', bundle.namelist())
                self.assertFalse(any('.git/' in name or 'firmware/' in name for name in bundle.namelist()))
                manifest = json.loads(bundle.read('Clawdy/MANIFEST.json'))
                for name, digest in manifest.items():
                    self.assertEqual(hashlib.sha256(bundle.read('Clawdy/'+name)).hexdigest(), digest)

    def test_missing_or_symlinked_bundle_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(ValueError):
                build_customer_bundle.build(root/'out.zip', root)
            (root/'install.py').symlink_to(root/'outside')
            with self.assertRaises(ValueError):
                build_customer_bundle.build(root/'out.zip', root)

    def test_provider_preflight_checks_all_configs_without_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cursor, gemini = root/'cursor.json', root/'gemini.json'
            cursor.write_text('{"version":1,"hooks":{}}')
            gemini.write_text('{"hooksConfig":{"enabled":false}}')
            with patch.object(provider_setup, 'settings_path', side_effect=lambda p: cursor if p == 'cursor' else gemini):
                with self.assertRaises(RuntimeError):
                    provider_setup.preflight(['cursor', 'gemini'])
            self.assertEqual(cursor.read_text(), '{"version":1,"hooks":{}}')
            self.assertEqual(gemini.read_text(), '{"hooksConfig":{"enabled":false}}')

    def test_enrolled_identity_mismatch_never_qualifies_as_board_report(self):
        reports = []
        link = BluetoothLink('toy', lambda: 'Y', reports.append, device_id='AABBCCDD')
        link.connected = True
        link.notified(None, json.dumps({'firmware':'traffic-nicenano-v1','device_id':'WRONG','transport':'ble'}).encode()+b'\n')
        self.assertEqual(reports, [])
        self.assertFalse(link.connected)
        self.assertIn('identity mismatch', link.last_error)
        link.notified(None, json.dumps({'firmware':'traffic-esp32c3-v1','device_id':'AABBCCDD','transport':'ble'}).encode()+b'\n')
        self.assertEqual(len(reports), 1)


if __name__ == '__main__':
    unittest.main()
