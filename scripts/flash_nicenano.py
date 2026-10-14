#!/usr/bin/env python3
"""Flash the tested nice!nano CircuitPython profile, preserving local backups."""
import argparse
import errno
import hashlib
from pathlib import Path
import shutil
import sys
import string
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://downloads.circuitpython.org/bin/nice_nano/en_US/adafruit-circuitpython-nice_nano-en_US-8.1.0.uf2'
SHA256 = '454ad2c9d24a82199fe3f59a977b9c04519c1901021ed639dd4a7ed90de7d3f5'
FILES = ('boot.py', 'ble_link.py', 'battery.py', 'connection_display.py', 'pwm_led.py', 'provider_icons.py', 'oled_display.py', 'session_count.py', 'code.py')

def auto_detect_circuitpy():
    if sys.platform == 'win32':
        roots = [Path(letter + ':/') for letter in string.ascii_uppercase]
    elif sys.platform == 'darwin':
        roots = list(Path('/Volumes').iterdir())
    else:
        raise RuntimeError('Specify --circuitpy on this platform.')
    candidates = [root for root in roots if (root / 'boot_out.txt').is_file()]
    if len(candidates) > 1:
        raise RuntimeError('Multiple CircuitPython drives found; specify --circuitpy explicitly.')
    return candidates[0] if candidates else None


def provision(boot_drive, circuitpy=None):
    # Bootloader flashing must work before CIRCUITPY exists. Discover after reset.
    if circuitpy is None and not boot_drive:
        circuitpy = auto_detect_circuitpy()
    if not boot_drive and (circuitpy is None or not circuitpy.is_dir()):
        raise RuntimeError('CIRCUITPY not found; connect a USB data cable or supply --boot-drive.')
    backup = ROOT / '.backups' / ('board-' + str(time.time_ns()))
    backup.mkdir(parents=True)
    if boot_drive:
        info = (boot_drive / 'INFO_UF2.TXT').read_text()
        if 'nRF52840-nicenano' not in info:
            raise RuntimeError('Bootloader board ID is not nRF52840-nicenano; select the correct firmware manually.')
        for name in ('INFO_UF2.TXT', 'CURRENT.UF2'):
            if (boot_drive / name).exists():
                shutil.copyfile(boot_drive / name, backup / name)
        firmware = backup / 'circuitpython-8.1.0.uf2'
        urllib.request.urlretrieve(URL, firmware)
        if hashlib.sha256(firmware.read_bytes()).hexdigest() != SHA256:
            raise RuntimeError('Firmware checksum mismatch; nothing has been flashed.')
        try:
            shutil.copyfile(firmware, boot_drive / 'traffic.uf2')
        except OSError as error:
            # Some UF2 bootloaders reset after the last block, before macOS closes the file.
            # Continue only for a vanished device; CIRCUITPY identity is checked below.
            if error.errno != errno.ENXIO or boot_drive.exists():
                raise
        for _ in range(120):
            if circuitpy is None:
                circuitpy = auto_detect_circuitpy()
            if circuitpy is not None and circuitpy.is_dir():
                break
            time.sleep(.5)
        else:
            raise RuntimeError('CIRCUITPY did not appear. Preserve backup and inspect the board; do not guess another UF2.')
    if not circuitpy.is_dir():
        raise RuntimeError('CIRCUITPY is missing. Enter UF2 bootloader and supply --boot-drive.')
    boot_info = (circuitpy / 'boot_out.txt').read_text()
    if boot_drive and 'CircuitPython 8.1.0' not in boot_info:
        raise RuntimeError('Expected CircuitPython version did not boot; inspect the preserved backup.')
    if 'nice!nano' not in boot_info and 'nice_nano' not in boot_info:
        raise RuntimeError('CIRCUITPY is not the expected nice!nano board.')
    for name in (*FILES, 'hardware_config.json', 'battery_config.json'):
        if (circuitpy / name).exists():
            shutil.copyfile(circuitpy / name, backup / name)
    # Install dependencies before code.py, which triggers an automatic reload.
    for name in FILES:
        shutil.copyfile(ROOT / 'firmware' / 'nicenano' / name, circuitpy / name)
    print('Firmware installed. Backup: ' + str(backup))
    print('Press RESET once (or unplug/replug USB) so boot.py configures the dedicated serial port.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--boot-drive', type=Path, help='Mounted NICENANO volume; downloads and flashes UF2')
    parser.add_argument('--circuitpy', type=Path, default=None)
    args = parser.parse_args()
    provision(args.boot_drive, args.circuitpy)
