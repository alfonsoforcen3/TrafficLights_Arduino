#!/usr/bin/env python3
"""Build a PRIVATE review candidate from an explicit allowlist; never publish."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'install.py', 'manage_hooks.py', 'scripts/onboard.py',
    'scripts/device_identity.py', 'scripts/platform_support.py', 'scripts/migrate_hook_runtime.py',
    'scripts/codex_setup.py', 'scripts/claude_setup.py', 'scripts/provider_setup.py',
    'scripts/traffic.py', 'scripts/bridge.py', 'scripts/ble_transport.py',
    'scripts/dashboard.py', 'scripts/windows_service.py', 'scripts/bluetooth_app.py',
    'scripts/build_bluetooth_app.py', 'scripts/verify_hardware.py',
    'web/index.html', 'web/style.css', 'web/app.js',
)


def build(destination, root=ROOT):
    """Nothing is selected by directory recursion, Git state or ignore patterns."""
    root, destination = Path(root).resolve(), Path(destination)
    manifest = {}
    content = {}
    for name in FILES:
        source = root / name
        if source.is_symlink() or not source.is_file() or root not in source.resolve().parents:
            raise ValueError('Missing or unsafe release input: ' + name)
        content[name] = source.read_bytes()
        manifest[name] = hashlib.sha256(content[name]).hexdigest()
    guide = (root/'docs/CUSTOMER_SETUP.md').read_bytes()
    content['README.md'] = guide
    content['AGENTS.md'] = (root/'docs/CUSTOMER_AGENT.md').read_bytes()
    content['DISTRIBUTION.txt'] = (
        'PRIVATE REVIEW CANDIDATE — NOT A CONSUMER RELEASE\n'
        'Contains readable Python implementation. Publication requires owner approval.\n'
        'No open-source license or distribution rights are granted by this bundle.\n'
        'Third-party packages are downloaded separately from PyPI under their own terms.\n'
        'This is not a signed/notarized standalone installer.\n').encode('utf-8')
    for name, data in content.items():
        manifest[name] = hashlib.sha256(data).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(content.items()):
            archive.writestr('Clawdy/'+name, data)
        archive.writestr('Clawdy/MANIFEST.json', json.dumps(manifest, sort_keys=True, indent=2)+'\n')
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(destination.suffix+'.sha256').write_text(digest+'  '+destination.name+'\n')
    return digest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'dist/clawdy-private-candidate.zip')
    args = parser.parse_args()
    print(build(args.output), args.output)
