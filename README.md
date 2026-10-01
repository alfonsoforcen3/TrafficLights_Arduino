# Bluetooth traffic light for Codex

A physical green / amber / red indicator for locally running Codex and ChatGPT Work chats. The tested wireless build uses a nice!nano-compatible nRF52840 board and a macOS Bluetooth login helper.

| Light | Meaning |
| --- | --- |
| Green | All tracked chats are ready or finished |
| Amber | At least one chat is working |
| Blinking red | Approval or a supported input request is pending |
| Solid red | An explicit error signal was received |

The bridge combines concurrent chats with priority: input → error → working → ready. A failed shell command does not automatically mean a red error; see [hooks](HOOKS_GUIDE.md).

## Start here

Give your agent this prompt:

> Clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git, read AGENTS.md and INSTALL.md, and install the macOS Bluetooth traffic light for my board. Verify the actual board and its wiring, preserve my existing hooks, and tell me when I need to approve macOS Bluetooth access or Codex hook trust. Do not report success until the board acknowledges commands over BLE and I confirm the LEDs physically light.

Then follow [INSTALL.md](INSTALL.md). The installer creates its own Python environment, discovers your board's name, installs the Mac login helper, and writes machine-local hook commands. It does not bypass OS permissions or hook trust.

## Documentation

- [Installation and agent workflow](INSTALL.md)
- [Board, LEDs, pin numbers, and flashing](docs/HARDWARE.md)
- [Bluetooth architecture and automatic recovery](docs/BLUETOOTH.md)
- [Hooks, permissions, and removal](HOOKS_GUIDE.md)
- [Multiple chats, priority, and transition timing](docs/MULTIPLE_CHATS.md)
- [Battery, switch, and charging](docs/BATTERY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Supported and unverified platforms](docs/COMPATIBILITY.md)
- [Tester acceptance checks](docs/TESTING.md)
- [Development and release workflow](docs/DEVELOPMENT.md)
- [Iteration history](CHANGELOG.md)

## Commands

```bash
python3 install.py                       # macOS BLE installation; USB discovery on first install
python3 install.py --ble-name TrafficLight-ABCD  # already provisioned board, exact name
python3 install.py --no-hooks            # update service without changing approved hooks
python3 manage_hooks.py status
python3 scripts/verify_hardware.py       # test through the installed bridge
python3 scripts/codex_setup.py usb       # switch back to USB
python3 scripts/codex_setup.py bluetooth # return to previously configured BLE device
python3 manage_hooks.py disable          # disable owned hooks and the login service
```

Firmware is in `firmware/nicenano/`; the original Arduino sketch in `firmware/traffic_light/` is a separate wired profile. No batteries, user configuration, credentials, generated apps, or downloaded firmware binaries are committed. The `claude-mascot-3d` checkout on the development machine is a separate repository and is not part of this release.

This is a tester iteration. Confirm the exact board and battery charging circuit before treating a clone as equivalent to a genuine nice!nano. Battery runtime, physical repeated battery switch cycles, other operating systems, and production distribution/signing are not yet certified or measured.
