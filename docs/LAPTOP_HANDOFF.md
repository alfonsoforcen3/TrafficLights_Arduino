# Release a Clawdy and connect another Mac

## Agent scope

Use this procedure when the user asks to release a board, switch laptops, or connect an already flashed unit. Do not enable the bridge just because this repository is opened. Coordinate one active Mac per board. Do not reflash a working unit for a laptop handoff, reset its per-unit configuration, or invent a new Bluetooth name.

## Release the old Mac

After normal installation, use the installed environment so maintenance scripts have their dependencies:

```bash
~/.local/share/trafficlights/venv/bin/python manage_hooks.py disable
```

This removes repository-owned provider hooks and the login service, preserving unrelated settings. It intentionally keeps the runtime environment, connection configuration, session records, firmware, per-board profile and backups. This is a full integration disable, not merely a temporary Bluetooth disconnect. Re-enabling later may require normal provider hook review. Running provider sessions may retain cached hook definitions until restarted; those definitions do not restart the BLE bridge. Move USB power away from the old Mac as well if a complete physical handoff is intended.

Verify that the login service is absent and the TCP bridge has no listener:

```bash
launchctl print gui/$(id -u)/local.trafficlights.bridge
lsof -nP -iTCP:8765 -sTCP:LISTEN
```

Expected: launchctl says the service was not found; lsof prints no listener. These commands may return nonzero for that expected absence. If a manually started bridge still exists, identify its process/checkout and stop that specific process; do not kill unrelated Python apps or Bluetooth services. A powered board should enter its simultaneous searching blink. Ask the user to confirm the physical indication. Do not claim another Mac connected until it reports BLE hardware delivery.

## Set up the new Mac

The source repository is private and requires an authorized GitHub account. In a stable directory:

```bash
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
python3 install.py --ble-name "first clawdy"
python3 manage_hooks.py status
python3 scripts/verify_hardware.py
```

Replace the name for another unit with its actual name. Read INSTALL.md and provider documentation first. The installer sets up its own environment, service and detected local providers. Allow Traffic Light Bridge Bluetooth access using macOS's normal dialog, and review provider hooks/trust; never bypass privacy/trust stores or request passwords in chat. Keep the board powered and nearby. Its USB cable does not need to carry data to the new Mac.

Require hardware_connected=true, transport=ble, a ble:// peer, current board reports and visible LED confirmation. The board plays its connection sequence then tracks the new Mac's sessions. Repeat documented restart/power-cycle tests as appropriate; record tests actually performed. Once set up, the local dashboard is http://127.0.0.1:8766/ on that Mac.

## Return to the original Mac

Release the other Mac first. Run `python3 install.py --ble-name "first clawdy"` on the original Mac to reinstall hooks/service and complete normal permission/hook review. `--no-hooks` is appropriate only when those hook definitions already exist and remain approved; it will not restore hooks removed during release.

## Known first clawdy profile

- BLE name: `first clawdy` (exact lower-case name, including the space).
- Green: P0.09, silkscreen `009`, appears as `600` upside down; amber P1.11; red P1.13.
- Board-ID nRF52840-nicenano; CircuitPython 8.1.0; profile lives in hardware_config.json on the board.
- Battery percentage and charging status remain unverified; a laptop handoff does not resolve those hardware limitations.

## Handoff record — 2026-10-06

The user requested release from the original Mac. The disable command removed owned hooks and login service. Service absence and no TCP 8765 listener were verified. The board firmware/profile were not changed. The second laptop's installation, Bluetooth connection and visible searching blink have not yet been verified in this chat.
