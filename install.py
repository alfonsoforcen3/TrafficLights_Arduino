#!/usr/bin/env python3
"""Install the native macOS/Windows traffic-light bridge and detected local provider adapters without system-wide pip changes."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import venv

ROOT = Path(__file__).resolve().parent
RUNTIME = Path.home() / '.local' / 'share' / 'trafficlights'

def discover_name():
    import serial
    from serial.tools import list_ports
    boards = [p for p in list_ports.comports() if p.vid == 0x239A and p.pid == 0x80B4]
    if len(boards) != 1:
        raise RuntimeError('Connect exactly one provisioned nice!nano by USB, or supply --ble-name from its advertisement.')
    with serial.Serial(boards[0].device, 115200, timeout=.1) as device:
        device.write(b'Q')
        buffer = b''
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            buffer += device.read(4096)
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                try:
                    report = json.loads(line)
                except ValueError:
                    continue
                if report.get('firmware') == 'traffic-nicenano-v1' and report.get('ble_name'):
                    if report.get('ble_error'):
                        raise RuntimeError(report['ble_error'])
                    return report['ble_name']
    raise RuntimeError('No traffic-light firmware acknowledgement. Provision firmware and reset the board first.')

def main():
    if '--onboard' in sys.argv[1:]:
        from scripts.onboard import run_cli as onboard
        return onboard([arg for arg in sys.argv[1:] if arg != '--onboard'])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transport', choices=['ble', 'serial'], default='ble')
    parser.add_argument('--ble-name', help='Exact TrafficLight-XXXX advertisement; otherwise discover via USB')
    parser.add_argument('--device-id', help='Verified immutable board identity from customer enrollment')
    parser.add_argument('--providers', nargs='+', choices=['codex', 'claude', 'gemini', 'cursor'],
                        help='Override auto-detection; install only selected local provider hooks')
    parser.add_argument('--no-hooks', action='store_true', help='Update connection/service only, preserving hook definitions')
    args = parser.parse_args()
    from scripts.platform_support import require_platform, venv_python
    try:
        system = require_platform()
    except RuntimeError as error:
        raise SystemExit(str(error))
    print('Detected operating system:', system)
    python = venv_python(RUNTIME)
    if Path(sys.prefix) != RUNTIME / 'venv':
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(RUNTIME / 'venv')
        subprocess.run([str(python), '-m', 'pip', 'install', 'pyserial==3.5'], check=True)
        subprocess.run([str(python), str(ROOT / 'install.py'), *sys.argv[1:]], check=True)
        return
    from scripts import codex_setup
    config_path = RUNTIME / 'connection.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    name = args.ble_name or config.get('ble_name')
    if args.transport == 'ble' and not name:
        name = discover_name()
    from scripts import provider_setup
    providers = args.providers or list(provider_setup.detect())
    if not args.no_hooks:
        provider_setup.preflight(providers)
    codex_setup.install_service(args.transport, name, device_id=args.device_id)
    if not args.no_hooks:
        print('Installing detected/selected hooks:', ', '.join(providers) or 'none')
        for provider in providers:
            provider_setup.configure(provider)
    print('Installed transport:', args.transport, '| Bluetooth name:', name)
    print('Review installed hooks in each provider and allow Bluetooth access if prompted.')
    print('Run python3 manage_hooks.py status. A running service is not proof the board or hooks are ready.')

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, TimeoutError, subprocess.CalledProcessError) as error:
        print('Clawdy installation stopped: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
