# Clawdy website and local battery telemetry

## Requirements and scope

The customer QR keeps its existing `https://alfonsoforcen3.github.io/clawd-mascot-3d/#setup` destination. Clawdy is the default companion; CyberDuck is the only alternate. Product/checkout/installer controls are previews and collect no information. The Mac-first local dashboard uses real board data only. Signed installer distribution and commerce remain release gates.

## Design

The Mac bridge serves the same HTML/CSS/JavaScript at `http://127.0.0.1:8766/`. The public website links to this local dashboard; it does not fetch private telemetry cross-origin or upload data. Loopback binding, strict Host validation, no CORS, restricted routes, and a content security policy protect the read-only API. No prompts, session identifiers, or hook payloads enter the dashboard API. A dashboard port conflict does not stop the light bridge.

`V` requests an ADC sample without changing LED state. The BLE bridge requests a sample upon connection and every 60 seconds. Normal reports reuse the sample cache. The website checks its local API every five seconds. Disconnects and missing/stale reports remove live values. History is bounded to 120 samples and is not persisted or uploaded.

## Hardware limitations

The genuine nice!nano documentation identifies P0.04/AIN2 as battery ADC: https://nicekeyboards.com/docs/nice-nano/pinout-schematic/ . This prototype is a clone. Its divider, charger IC/current, protection and charge termination have not been verified. Firmware reports the real ADC sensor voltage, with battery voltage/percentage null until calibrated. USB presence, rising voltage, or a percentage is not proof of safe charging. The existing 3.7 V / 300 mAh battery's 25C marking specifies discharge capability, not permissible charge current.

For verification, use a multimeter (a voltage meter with two probes), read the cell's voltage independently, identify the board divider and compare multiple points. Never connect a battery directly to an ADC/GPIO. After hardware verification, create `/battery_config.json` on CIRCUITPY with `{"verified": true, "divider_ratio": <measured and verified ratio>}` and reload. Do not copy another board's ratio. The returned percentage is an approximate single-cell resting-voltage estimate, especially inaccurate while charging or under load. `charging` remains unknown; the board has no verified charger-state input.

## Installation and maintenance

Factory provisioning copies `battery.py` before `code.py` along with existing firmware files. Preserve existing files and any calibration. `install.py --no-hooks` copies dashboard code/assets to the stable runtime without changing provider hooks. Updating the bridge must retain macOS Bluetooth approval and approved hooks. The UI does not change lights or invoke hardware tests.

Customer website files are also maintained in the currently private independent mascot repository at its root and `docs/` to preserve existing hosting layouts. Only frontend assets are copied there; implementation and calibration remain in the implementation repository. GitHub Pages is currently disabled; the QR destination requires a future hosting release. Do not stage unrelated model/STL work when updating this site.

## Verification: 2026-10-02

- Requirements, implementation and hardware limitations recorded here.
- 22 automated tests passed, including missing/disconnected/stale battery data, private data omission, hostile Host rejection, route restrictions, and calibration gating.
- JavaScript syntax checked; Clawdy default and CyberDuck toggle visually checked in the Mac browser.
- Existing firmware preserved in ignored local backups; telemetry source installed on the identified nice_nano CircuitPython 8.1.0 board.
- Real BLE battery sensor reports and GPIO acknowledgements observed; this is not human confirmation of visible LEDs.
- Battery percentage calibration, battery-only power-cycle with this iteration, charger current/temperature/termination, signed installer and public QR deployment are not verified by these checks.

## Release gates

Verify clone hardware and per-board voltage conversion before presenting percentage to customers. Validate charging with an appropriate cell and charger specifications. Perform battery-only reconnection and Mac restart tests. Sign/notarize the standalone installer. Verify public QR deployment independently; local preview is not a public release.
