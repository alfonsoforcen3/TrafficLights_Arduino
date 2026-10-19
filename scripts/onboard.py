#!/usr/bin/env python3
"""Guided setup for a powered, factory-flashed Clawdy. USB data is unnecessary."""
import argparse
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time
import venv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import provider_setup, device_identity
from scripts.platform_support import require_platform, venv_python

RUNTIME = Path.home() / '.local/share/trafficlights'


class WizardUI:
    """Small accessible terminal presentation; no cursor control or dependencies."""
    def __init__(self, no_color=False):
        stream = sys.stdout
        windows_ansi = (os.name != 'nt' or os.environ.get('WT_SESSION')
                        or os.environ.get('ANSICON') or os.environ.get('TERM_PROGRAM') == 'vscode'
                        or os.environ.get('TERM', '').startswith('xterm'))
        self.color = (not no_color and 'NO_COLOR' not in os.environ
                      and os.environ.get('TERM') != 'dumb'
                      and bool(getattr(stream, 'isatty', lambda: False)())
                      and bool(windows_ansi))

    @staticmethod
    def text(value):
        # Nearby advertisements are not trusted terminal control sequences.
        return ''.join(c if c.isprintable() else '\\x%02x' % ord(c) for c in str(value))

    def paint(self, value, code):
        text = self.text(value)
        return '\033[' + code + 'm' + text + '\033[0m' if self.color else text

    def banner(self, laptop, preview=False):
        print()
        print(self.paint('  C L A W D Y', '1;36'))
        print('  A little companion for your AI work.')
        print(self.paint('  ' + ('Offline preview' if preview else 'Bluetooth setup')
                         + ' | ' + self.text(laptop), '2'))
        print(self.paint('  ' + '-' * 54, '2'))
        if preview:
            self.status('info', 'Preview only: no Bluetooth scan, downloads or changes.')

    def phase(self, number, title):
        print()
        print(self.paint('  %d/5  %s' % (number, title), '1;36'))

    def detail(self, label, value):
        print('       ' + self.paint(label + ':', '2') + ' ' + self.text(value))

    def status(self, state, message):
        labels = {'ok':('OK', '32'), 'pending':('PENDING', '33'),
                  'info':('INFO', '36'), 'working':('...', '36')}
        label, color = labels[state]
        print('  ' + self.paint('[' + label + ']', color) + ' ' + self.text(message), flush=True)


def make_name(laptop, nickname):
    """Preview the shared naming policy; the suffix needs verified device identity."""
    return device_identity.make_device_name(laptop, nickname, '00000000')[:-8] + '<UID8>'


def confirm(message, yes=False, input_fn=input):
    if yes:
        return True
    if not sys.stdin.isatty():
        raise RuntimeError('Noninteractive setup needs --yes plus explicit --ble-name and --nickname (or --keep-name).')
    return input_fn(message + ' [y/N] ').strip().lower() in ('y', 'yes')


def select_device(devices, exact_name=None, address=None, input_fn=input):
    candidates = [d for d in devices if (not exact_name or d['name'] == exact_name)
                  and (not address or d['address'] == address)]
    if not candidates:
        raise RuntimeError('No matching advertising Clawdy. Check power, Bluetooth permission, range, and that another laptop is disconnected.')
    if exact_name and len(candidates) == 1:
        return candidates[0]
    if not sys.stdin.isatty():
        raise RuntimeError('Select one exact --ble-name and, for duplicate names, --device-address. No arbitrary device will be chosen.')
    print('       Nearby devices (Clawdy firmware is checked next):')
    for index, device in enumerate(candidates, 1):
        print('       [%d] %s  (%s)' % (index, WizardUI.text(device['name']), WizardUI.text(device['address'])))
    try:
        choice = int(input_fn('Which toy is yours? Enter its number: '))
    except ValueError:
        raise RuntimeError('Enter a listed device number.')
    if not 1 <= choice <= len(candidates):
        raise RuntimeError('Device selection is out of range.')
    return candidates[choice - 1]


def choose_providers(args, input_fn=input):
    if args.no_hooks:
        return []
    if args.providers is not None:
        return args.providers
    found = list(provider_setup.detect())
    WizardUI(getattr(args, 'no_color', False)).detail('Detected AI apps', ', '.join(found) or 'none')
    if args.yes or args.dry_run:
        return found
    if not sys.stdin.isatty():
        raise RuntimeError('Use --providers or --no-hooks for noninteractive setup.')
    text = input_fn('Providers (codex claude gemini cursor), Enter for detected, or none: ').strip().lower()
    if text == 'none':
        return []
    selected = text.split() if text else found
    if any(p not in provider_setup.SUPPORTED for p in selected):
        raise ValueError('Choose only codex, claude, gemini, cursor, or none.')
    return list(dict.fromkeys(selected))


def installer_command(name, providers, device_id=None):
    command = [sys.executable, str(ROOT / 'install.py'), '--ble-name', name]
    if device_id:
        command += ['--device-id', device_id]
    return command + (['--providers', *providers] if providers else ['--no-hooks'])


def ensure_dependencies(args, argv):
    if importlib.util.find_spec('bleak') is not None:
        return False
    ui = WizardUI(getattr(args, 'no_color', False))
    ui.status('info', 'Bluetooth setup needs a private Python environment and packages from PyPI.')
    if not confirm('Create ~/.local/share/trafficlights/venv and download Bluetooth dependencies?', args.yes):
        raise RuntimeError('Setup cancelled before dependency installation.')
    python = venv_python(RUNTIME)
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(RUNTIME / 'venv')
    ui.status('working', 'Preparing Bluetooth dependencies...')
    subprocess.run([str(python), '-m', 'pip', 'install', 'bleak==0.22.3', 'pyserial==3.5'], check=True)
    ui.status('ok', 'Dependencies ready. Continuing setup in the private environment.')
    subprocess.run([str(python), str(Path(__file__).resolve()), *argv], check=True)
    return True


def human_confirmation(message, input_fn=input):
    """--yes accepts install changes; it cannot assert a physical observation."""
    if not sys.stdin.isatty():
        return False
    return input_fn(message + ' [y/N] ').strip().lower() in ('y', 'yes')


def verify_install(device_id=None, timeout=30, ui=None):
    from scripts import verify_hardware
    ui = ui or WizardUI()
    ui.status('info', 'Allow the normal Bluetooth request for Traffic Light Bridge.')
    ui.detail('Hook permissions', 'Review hooks and workspace trust in each selected AI app.')
    if sys.stdin.isatty():
        input('Press Enter after granting Bluetooth permission to test the lights: ')
    ui.status('working', 'Waiting for your Clawdy to acknowledge the Bluetooth connection...')
    deadline = time.monotonic() + timeout
    while True:
        try:
            status = verify_hardware.request({'action': 'status'})
            report = status.get('firmware_report') or {}
            if (status.get('hardware_connected') is True and status.get('transport') == 'ble'
                    and str(status.get('port', '')).startswith('ble://')
                    and report.get('transport') == 'ble'
                    and (not device_id or report.get('device_id') == device_id)):
                break
        except (OSError, ValueError):
            pass
        if time.monotonic() >= deadline:
            raise RuntimeError('Installed, but Bluetooth delivery is not verified. Grant Bluetooth permission, check power/range and other laptops, then run python3 manage_hooks.py status and python3 scripts/verify_hardware.py.')
        time.sleep(.5)
    ui.status('ok', 'Bluetooth identity and board connection verified.')
    ui.status('working', 'Checking red, amber, green, blinking red and off...')
    try:
        verify_hardware.verify('ble')
    except (AssertionError, OSError, ValueError) as error:
        raise RuntimeError('Installed, but LED acknowledgement test failed: ' + str(error)) from error
    if not human_confirmation('Did YOUR toy visibly show red, amber, green and blinking red during the test?'):
        ui.status('pending', 'Hardware acknowledgements passed; physical LED confirmation remains pending.')
        return False
    ui.status('ok', 'Clawdy is linked. Bluetooth and visible LEDs verified.')
    ui.detail('Next', 'Review hooks, then try a real prompt, completion and input request in each AI app.')
    ui.status('pending', 'Real-provider acceptance, power-cycle, and laptop restart tests remain pending until actually performed.')
    return True


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--ble-name', help='Exact current name printed on the device or seen in Bluetooth discovery')
    result.add_argument('--device-address', help='Disambiguate identical names using the address/UUID shown by discovery')
    result.add_argument('--nickname', help='Your chosen device name; paired with this laptop name')
    result.add_argument('--laptop-name', default=socket.gethostname().split('.')[0])
    result.add_argument('--keep-name', action='store_true', help='Keep the firmware advertisement unchanged')
    result.add_argument('--providers', nargs='+', choices=provider_setup.SUPPORTED)
    result.add_argument('--no-hooks', action='store_true')
    result.add_argument('--yes', action='store_true', help='Accept the displayed plan; explicit device/name required')
    result.add_argument('--no-color', action='store_true', help='Use plain terminal output (also honors NO_COLOR)')
    result.add_argument('--dry-run', action='store_true', help='Offline plan only: no scan, connection, downloads or changes')
    result.add_argument('--identified-device', action='store_true', help='Noninteractive assertion: you have already identified this exact physical device')
    result.add_argument('--skip-verification', action='store_true', help='Install only; leave LED/provider acceptance explicitly pending')
    result.add_argument('--scan-timeout', type=float, default=8.0)
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser().parse_args(argv)
    if args.keep_name and args.nickname:
        raise ValueError('Choose --nickname or --keep-name, not both.')
    if args.providers and args.no_hooks:
        raise ValueError('Choose --providers or --no-hooks, not both.')
    if not 1 <= args.scan_timeout <= 60:
        raise ValueError('Scan timeout must be between 1 and 60 seconds.')
    if (args.yes or args.dry_run) and (not args.ble_name or not (args.nickname or args.keep_name)):
        raise ValueError('--yes/--dry-run require --ble-name and --nickname or --keep-name.')
    ui = WizardUI(args.no_color)
    ui.banner(args.laptop_name, preview=args.dry_run)
    if not args.dry_run:
        ui.phase(1, 'Prepare your laptop')
        require_platform()
        # Fail explicit policy/configuration checks before downloading anything.
        # Bootstrap before interactive choices, since it relaunches with argv.
        if args.providers is not None or args.no_hooks:
            provider_setup.preflight(args.providers or [])
        if ensure_dependencies(args, argv):
            return 0
        ui.status('ok', 'Bluetooth tools ready. Your toy only needs power; no USB data cable.')
    ui.phase(2, 'Choose your setup')
    providers = choose_providers(args)
    if not args.dry_run:
        provider_setup.preflight(providers)
    nickname = args.nickname
    if not nickname and not args.keep_name:
        if not sys.stdin.isatty():
            raise RuntimeError('Supply --nickname or --keep-name.')
        nickname = input('What would you like to call your Clawdy? ').strip()
    desired = make_name(args.laptop_name, nickname) if nickname else args.ble_name
    ui.detail('Bluetooth name preview (UID pending)' if nickname else 'Bluetooth name',
              desired or 'Choose from nearby devices')
    if nickname:
        ui.detail('Naming', 'Laptop + nickname + unique device suffix; shortened to fit Bluetooth.')
    ui.detail('AI app hooks', ', '.join(providers) or 'none (companion only)')
    ui.detail('Access', 'Normal Bluetooth permission and app hook/trust review are required.')
    if args.dry_run:
        print(json.dumps({'dry_run': True, 'current_name': args.ble_name, 'requested_name': desired,
                          'installer': None if nickname else installer_command(desired, providers),
                          'rename_requires_firmware_support': bool(nickname),
                          'compatibility': 'Only verified supported UART firmware; board model alone is insufficient. ESP32 acceptance pending.',
                          'final_name_requires_device_identity': bool(nickname)}, indent=2))
        return 0
    ui.phase(3, 'Find your Clawdy')
    ui.status('info', 'Power on your toy nearby and disconnect its previous controlling laptop.')
    ui.status('working', 'Looking for nearby toys for up to %g seconds...' % args.scan_timeout)
    devices = asyncio.run(device_identity.discover_candidates(timeout=args.scan_timeout))
    selected = select_device(devices, args.ble_name, args.device_address)
    if not desired:
        desired = selected['name']
    ui.detail('Selected toy', selected['name'])
    ui.detail('Discovery ID', selected['address'])
    ui.status('info', 'Next: verify this toy, apply your naming choice, and install the companion and selected hooks.')
    if not confirm('Apply this setup?', args.yes):
        ui.status('info', 'Cancelled; device and host settings unchanged.')
        return 0
    ui.phase(4, 'Make it yours')
    ui.status('working', 'Checking the selected toy firmware and identity...')
    report = asyncio.run(device_identity.inspect_device(selected['address']))
    final_name = report.get('ble_name')
    if not final_name:
        raise RuntimeError('Verified board did not report its Bluetooth name.')
    if not sys.stdin.isatty() and not args.identified_device:
        raise RuntimeError('Physical selection needs confirmation. Run interactively or provide --identified-device only after independently identifying this exact toy.')
    ui.status('info', 'Watch YOUR toy: red, amber, green, then its previous state.')
    asyncio.run(device_identity.identify_device(selected['address'], report.get('device_id')))
    if not args.identified_device and not human_confirmation('Did YOUR toy show that red/amber/green sequence?'):
        raise RuntimeError('Device was not physically confirmed; no rename or host installation performed.')
    if nickname:
        if not report.get('rename_supported') or report.get('identity_protocol') != 1:
            raise RuntimeError('This firmware cannot persist a Bluetooth rename. Rerun with --keep-name; factory firmware update is required for naming.')
        desired = device_identity.make_device_name(args.laptop_name, nickname, report['device_id'])
        ui.detail('Unique Bluetooth name', desired)
        ui.status('working', 'Saving the name on your toy...')
        ack = asyncio.run(device_identity.rename_device(selected['address'], desired, report['device_id']))
        if not ack.get('ok') or not ack.get('persistent') or ack.get('ble_name') != desired:
            raise RuntimeError('Board did not acknowledge a persistent rename; host installation stopped.')
        final_name = desired
        ui.status('ok', 'Your toy confirmed the saved name.')
    else:
        ui.status('ok', 'Keeping your toy name: ' + final_name)
    ui.phase(5, 'Install & check')
    ui.status('working', 'Installing the local companion and your selected hooks...')
    subprocess.run(installer_command(final_name, providers, report.get('device_id')), check=True)
    if args.skip_verification:
        ui.status('pending', 'Installed; Bluetooth delivery, visible LEDs and real provider acceptance remain unverified.')
        ui.detail('Check next', 'python3 manage_hooks.py status; python3 scripts/verify_hardware.py')
        return 0
    return 0 if verify_install(report.get('device_id'), ui=ui) else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, TimeoutError, subprocess.CalledProcessError) as error:
        print('Clawdy setup stopped: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
