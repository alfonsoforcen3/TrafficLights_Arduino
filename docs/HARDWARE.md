# Hardware and factory provisioning

The verified prototype has an nRF52840 and identifies its bootloader as nice!nano, Board-ID nRF52840-nicenano, UF2 0.6.0 / SoftDevice S140 6.1.1. A bootloader identity does not prove a clone has the genuine board's charger or protection circuit. Verify the supplier schematic and labels for each production board revision.

| LED | Nordic GPIO | Connection |
| --- | --- | --- |
| Green | P0.10 | GPIO → 220–330 Ω resistor → LED anode |
| Amber | P1.11 | GPIO → 220–330 Ω resistor → LED anode |
| Red | P1.13 | GPIO → 220–330 Ω resistor → LED anode |
| All cathodes | GND | Common ground |

P0.10 means port 0, pin 10. Do not substitute Arduino pin 10. Fit one resistor per LED. Check polarity, common ground, soldered headers, and breadboard row continuity. A board resting over unsoldered headers is not a connection; software output reports cannot detect that defect.

For soldering this board follow its supplier's temperature and dwell guidance. The genuine nice!nano manufacturer specifies approximately 270–300°C; our earlier generic soldering-iron advice was not board-specific. See [manufacturer preparation](https://nicekeyboards.com/docs/nice-nano/getting-started/). Do not use header locations from another revision as battery terminal evidence.

## Factory load

Use scripts/flash_nicenano.py as described in INSTALL.md. It checks the board ID and backs up CURRENT.UF2 / existing files. The pinned official UF2 is:

- URL: https://downloads.circuitpython.org/bin/nice_nano/en_US/adafruit-circuitpython-nice_nano-en_US-8.1.0.uf2
- SHA-256: `454ad2c9d24a82199fe3f59a977b9c04519c1901021ed639dd4a7ed90de7d3f5`
- Sources: [CircuitPython board page](https://circuitpython.org/board/nice_nano/) and [manufacturer flashing instructions](https://nicekeyboards.com/docs/nice-nano/getting-started/).

Copy boot.py, ble_link.py, and code.py; reset once after boot.py changes. CircuitPython enables USB data only, with its console disabled. Firmware needs only built-in libraries. It also advertises Nordic UART BLE.

USB/BLE commands are G, Y, R, B, O, T; Q returns a newline JSON GPIO report. USB-only X resets the board for maintenance. T is a firmware light cycle; the host acceptance helper uses explicit states instead.

The BLE name comes from the CPU UID suffix. Read the actual Q response or BLE advertisement and label each unit with its exact TrafficLight-XXXX name. Check names are unique within each batch; the current four-hex suffix is not a production serial-number system. Record batch ID, supplier/revision, firmware commit, name, wiring, visual LED results, and battery/charging acceptance before shipment. Do not ship devices that only pass software checks.

Customers should receive a pre-flashed, assembled, tested unit. USB provisioning is for the factory, firmware updates, and recovery—not ordinary customer onboarding.
