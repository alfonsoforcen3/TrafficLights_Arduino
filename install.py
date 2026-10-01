#!/usr/bin/env python3
"""Install the tested macOS Codex traffic-light profile without system-wide pip changes."""
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transport', choices=['ble', 'serial'], default='ble')
    parser.add_argument('--ble-name', help='Exact TrafficLight-XXXX advertisement; otherwise discover via USB')
    parser.add_argument('--no-hooks', action='store_true', help='Update connection/service only, preserving hook definitions')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        raise SystemExit('This installer supports macOS. See docs/COMPATIBILITY.md for manual/legacy platforms.')
    python = RUNTIME / 'venv' / 'bin' / 'python'
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
    codex_setup.install_service(args.transport, name)
    if not args.no_hooks:
        codex_setup.enable(install_login_service=False)
    print('Installed transport:', args.transport, '| Bluetooth name:', name)
    print('Review/trust Traffic light hooks in Codex; allow Traffic Light Bridge Bluetooth access in macOS.')
    print('Run python3 manage_hooks.py status. A running service is not proof the board or hooks are ready.')

if __name__ == '__main__':
    main()
