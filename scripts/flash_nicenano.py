#!/usr/bin/env python3
"""Flash the tested nice!nano CircuitPython profile, preserving local backups."""
import argparse
import hashlib
from pathlib import Path
import shutil
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://downloads.circuitpython.org/bin/nice_nano/en_US/adafruit-circuitpython-nice_nano-en_US-8.1.0.uf2'
SHA256 = '454ad2c9d24a82199fe3f59a977b9c04519c1901021ed639dd4a7ed90de7d3f5'
FILES = ('boot.py', 'ble_link.py', 'code.py')

def provision(boot_drive, circuitpy):
    backup = ROOT / '.backups' / ('board-' + str(time.time_ns()))
    backup.mkdir(parents=True)
    if boot_drive:
        info = (boot_drive / 'INFO_UF2.TXT').read_text()
        if 'nRF52840-nicenano' not in info:
            raise RuntimeError('Bootloader board ID is not nRF52840-nicenano; select the correct firmware manually.')
        for name in ('INFO_UF2.TXT', 'CURRENT.UF2'):
            if (boot_drive / name).exists():
                shutil.copy2(boot_drive / name, backup / name)
        firmware = backup / 'circuitpython-8.1.0.uf2'
        urllib.request.urlretrieve(URL, firmware)
        if hashlib.sha256(firmware.read_bytes()).hexdigest() != SHA256:
            raise RuntimeError('Firmware checksum mismatch; nothing has been flashed.')
        shutil.copyfile(firmware, boot_drive / 'traffic.uf2')
        for _ in range(120):
            if circuitpy.is_dir():
                break
            time.sleep(.5)
        else:
            raise RuntimeError('CIRCUITPY did not appear. Preserve backup and inspect the board; do not guess another UF2.')
    if not circuitpy.is_dir():
        raise RuntimeError('CIRCUITPY is missing. Enter UF2 bootloader and supply --boot-drive.')
    boot_info = (circuitpy / 'boot_out.txt').read_text()
    if 'nice!nano' not in boot_info and 'nice_nano' not in boot_info:
        raise RuntimeError('CIRCUITPY is not the expected nice!nano board.')
    for name in FILES:
        if (circuitpy / name).exists():
            shutil.copy2(circuitpy / name, backup / name)
    # Install dependencies before code.py, which triggers an automatic reload.
    for name in FILES:
        shutil.copyfile(ROOT / 'firmware' / 'nicenano' / name, circuitpy / name)
    print('Firmware installed. Backup: ' + str(backup))
    print('Press RESET once (or unplug/replug USB) so boot.py configures the dedicated serial port.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--boot-drive', type=Path, help='Mounted NICENANO volume; downloads and flashes UF2')
    parser.add_argument('--circuitpy', type=Path, default=Path('/Volumes/CIRCUITPY'))
    args = parser.parse_args()
    provision(args.boot_drive, args.circuitpy)
