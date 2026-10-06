#!/usr/bin/env python3
"""Install/remove this project's Codex hooks and macOS login bridge service.

Hook trust is deliberately left to the app's normal hook review screen.
"""
import json
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import time

try:
    from scripts.platform_support import venv_python, hook_command
except ModuleNotFoundError:
    from platform_support import venv_python, hook_command

ROOT = Path(__file__).resolve().parents[1]
HOOKS = Path.home() / '.codex' / 'hooks.json'
SERVICE = 'local.trafficlights.bridge'
PLIST = Path.home() / 'Library' / 'LaunchAgents' / (SERVICE + '.plist')
RUNTIME = Path.home() / '.local' / 'share' / 'trafficlights'
MARKER = 'Traffic light:'

def read_hooks():
    if HOOKS.exists():
        return json.loads(HOOKS.read_text())
    return {'hooks': {}}

def remove_ours(data):
    for event, groups in list(data.get('hooks', {}).items()):
        retained = []
        for group in groups:
            group = dict(group)
            group['hooks'] = [h for h in group.get('hooks', [])
                              if not h.get('statusMessage', '').startswith(MARKER)]
            if group['hooks']:
                retained.append(group)
        if retained:
            data['hooks'][event] = retained
        else:
            del data['hooks'][event]

def save(data):
    HOOKS.parent.mkdir(parents=True, exist_ok=True)
    if HOOKS.exists():
        backup = ROOT / '.backups' / ('codex-hooks-' + str(time.time_ns()) + '.json')
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOOKS, backup)
    temporary = HOOKS.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(HOOKS)

def install_service(transport=None, ble_name=None):
    if sys.platform not in ('darwin', 'win32'):
        raise RuntimeError('Use native macOS or Windows Python.')
    RUNTIME.mkdir(parents=True, exist_ok=True)
    config_path = RUNTIME / 'connection.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {
        'transport': 'serial', 'ble_name': None}
    if transport:
        config['transport'] = transport
    if ble_name:
        config['ble_name'] = ble_name
    if config['transport'] == 'ble' and not config.get('ble_name'):
        raise RuntimeError('Run python3 install.py to discover your board, or provide --ble-name.')
    python = Path(sys.executable)
    if config['transport'] == 'ble':
        python = venv_python(RUNTIME)
        if not python.exists():
            subprocess.run([sys.executable, '-m', 'venv', str(RUNTIME / 'venv')], check=True)
        dependencies = ['bleak==0.22.3', 'pyserial==3.5']
        if sys.platform == 'darwin':
            dependencies += ['py2app==0.28.8', 'setuptools<71']
        subprocess.run([str(python), '-m', 'pip', 'install', *dependencies], check=True)
    if sys.platform == 'win32':
        try:
            from scripts.windows_service import install
        except ModuleNotFoundError:
            from windows_service import install
        install(ROOT, RUNTIME, python, config)
    config_path.write_text(json.dumps(config, indent=2) + '\n')
    if sys.platform == 'darwin':
        PLIST.parent.mkdir(parents=True, exist_ok=True)
        RUNTIME.mkdir(parents=True, exist_ok=True)
        # Login services cannot rely on access to macOS-protected Desktop folders.
        shutil.copy2(ROOT / 'scripts' / 'bridge.py', RUNTIME / 'bridge.py')
        shutil.copy2(ROOT / 'scripts' / 'ble_transport.py', RUNTIME / 'ble_transport.py')
        shutil.copy2(ROOT / 'scripts' / 'dashboard.py', RUNTIME / 'dashboard.py')
        shutil.copytree(ROOT / 'web', RUNTIME / 'web', dirs_exist_ok=True)
        program = [str(python), '-u', str(RUNTIME / 'bridge.py')]
        if config['transport'] == 'ble':
            for filename in ('bluetooth_app.py', 'build_bluetooth_app.py'):
                shutil.copy2(ROOT / 'scripts' / filename, RUNTIME / filename)
            app = RUNTIME / 'dist' / 'Traffic Light Bridge.app'
            if not app.exists():
                subprocess.run([str(python), 'build_bluetooth_app.py', 'py2app', '-A'],
                               cwd=RUNTIME, check=True)
            program = [str(app / 'Contents' / 'MacOS' / 'Traffic Light Bridge')]
        service = {'Label': SERVICE, 'ProgramArguments': program, 'RunAtLoad': True,
                   'KeepAlive': True, 'WorkingDirectory': str(RUNTIME),
                   'EnvironmentVariables': {'TRAFFIC_TRANSPORT': config['transport'],
                                            'TRAFFIC_BLE_NAME': config['ble_name']},
                   'StandardOutPath': str(RUNTIME / 'bridge.log'),
                   'StandardErrorPath': str(RUNTIME / 'bridge.log'), 'ThrottleInterval': 5}
        subprocess.run(['launchctl', 'bootout', 'gui/' + str(os.getuid()), str(PLIST)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        PLIST.write_bytes(plistlib.dumps(service))
        subprocess.run(['launchctl', 'bootstrap', 'gui/' + str(os.getuid()), str(PLIST)], check=True)

def enable(install_login_service=True):
    data = read_hooks()
    remove_ours(data)
    events = {'SessionStart': 'G', 'UserPromptSubmit': 'Y', 'PreToolUse': 'Y',
              'PostToolUse': 'Y', 'PermissionRequest': 'B', 'Stop': 'G',
              'Interrupt': 'G', 'SessionEnd': 'O'}
    hook_python = venv_python(RUNTIME)
    base = hook_command(hook_python if hook_python.exists() else sys.executable, ROOT / 'scripts' / 'traffic.py')
    for event, color in events.items():
        group = {'hooks': [{'type': 'command', 'command': base + ' ' + color,
                            'timeout': 3, 'statusMessage': MARKER + ' ' + event}]}
        if event in ('PreToolUse', 'PostToolUse', 'PermissionRequest'):
            group['matcher'] = '.*'
        data.setdefault('hooks', {}).setdefault(event, []).append(group)
    save(data)
    if install_login_service:
        install_service()
    print('Installed Codex hooks: ' + str(HOOKS))
    print('Review and trust the Traffic light hooks in the app Hooks settings (or CLI /hooks).')

def disable():
    try:
        from scripts import claude_setup
    except ModuleNotFoundError:
        import claude_setup
    if claude_setup.SETTINGS.exists():
        claude_setup.configure(False)
    try:
        from scripts import provider_setup
    except ModuleNotFoundError:
        import provider_setup
    for provider in ('gemini', 'cursor'):
        provider_setup.configure(provider, False)
    data = read_hooks()
    remove_ours(data)
    save(data)
    if sys.platform == 'win32':
        try:
            from scripts.windows_service import remove
        except ModuleNotFoundError:
            from windows_service import remove
        remove()
    if sys.platform == 'darwin' and PLIST.exists():
        subprocess.run(['launchctl', 'bootout', 'gui/' + str(os.getuid()), str(PLIST)], check=False)
        PLIST.unlink()
    if sys.platform != 'win32':
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'traffic.py'), 'O'],
                       stdin=subprocess.DEVNULL)
    print('Removed owned provider hooks and login service; unrelated hooks preserved.')

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'enable':
        enable()
    elif len(sys.argv) == 2 and sys.argv[1] == 'disable':
        disable()
    elif len(sys.argv) == 2 and sys.argv[1] in ('bluetooth', 'usb'):
        install_service('ble' if sys.argv[1] == 'bluetooth' else 'serial')
        print('Bridge transport set to ' + sys.argv[1] + '; existing hook definitions preserved.')
    else:
        raise SystemExit('Usage: codex_setup.py enable|disable|bluetooth|usb')
