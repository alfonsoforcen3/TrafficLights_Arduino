# Install the native desktop Bluetooth companion

For OS-specific install, hook activation, update and removal steps, start with
[Install and activate: Mac / Windows / Linux status](docs/INSTALL_ACTIVATE.md).
Linux/WSL activation is unsupported; the linked guide includes development tests.

The installer detects macOS or Windows. Follow the Mac instructions below or the [Windows guide](docs/windows/INSTALL.md). Linux/WSL installation is unsupported.

## 1. Prerequisites

- The nRF52840 board described in [hardware](docs/HARDWARE.md), wired with three LED resistors and soldered headers.
- A USB **data** cable for initial provisioning; Bluetooth for normal commands.
- macOS with Bluetooth enabled, Git, and Python 3 with `venv` and `pip`. The verified machine uses macOS 26.6.2 and Apple Command Line Tools Python 3.9.6. New Python/macOS combinations need the acceptance tests; they are not automatically verified.
- A supported local AI application: Codex/Work, Claude Code, Gemini CLI or Cursor Agent; see [provider evidence and limits](docs/PROVIDERS.md). Ordinary ChatGPT chat and cloud orchestration do not execute these local command hooks.
- Internet access to GitHub (clone/source), downloads.circuitpython.org (UF2), and PyPI/package file hosts (Python dependencies).

No OpenAI API key, hosted server, cloud subscription for the bridge, or administrator access to run the service is required. macOS may require user authentication when changing privacy permissions. Obtain Python/Git from their official distribution or Apple Command Line Tools if missing; agents should not silently accept license agreements.

## 2. Clone into a stable directory

```bash
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
```

Keep this directory: hook commands refer to its absolute local path. Read AGENTS.md before changing the user's environment.

**Shipped pre-flashed unit:** power it on and skip to step 4, using the Bluetooth name printed on its label. No USB data connection or flashing is required for normal customer setup.

## 3. Factory / DIY / recovery only: provision the board

Confirm the hardware profile and LED wiring first. Enter the UF2 bootloader by double tapping RESET; the NICENANO volume should appear. Confirm INFO_UF2.TXT contains `Board-ID: nRF52840-nicenano`.

```bash
python3 scripts/flash_nicenano.py --boot-drive /Volumes/NICENANO
```

This backs up existing firmware, downloads the official nice_nano CircuitPython 8.1.0 UF2, validates its SHA-256, flashes it, waits for CIRCUITPY, and copies boot.py, ble_link.py, battery.py, connection_display.py, pwm_led.py, provider_icons.py, oled_display.py, session_count.py, and code.py. Version 8.1.0 is pinned because this tested board has UF2 bootloader 0.6.0; it avoids a bootloader migration. This is a compatibility choice, not a claim that 8.1.0 is the latest release.

If CIRCUITPY already runs the correct profile, update its files without downloading/reflashing:

```bash
python3 scripts/flash_nicenano.py
```

**Press RESET once or unplug/replug after provisioning**, so boot.py enables the dedicated USB data port. Never disconnect while files are being copied. See [hardware](docs/HARDWARE.md) for sources, checksum, backup and recovery.

## 4. Install the host bridge and hooks

For a shipped unit, read the name on its label and run:

```bash
python3 install.py --ble-name TrafficLight-ABCD
```

Replace the example with the actual label. For a developer unit without a label, keep exactly one board connected by USB for first discovery:

```bash
python3 install.py
```

The installer creates an isolated environment under ~/.local/share/trafficlights/venv. It probes the board's `Q` response to learn its own TrafficLight-XXXX name; it never assumes the developer's board name. It installs a locally built Traffic Light Bridge app, a LaunchAgent that runs at **user login**, and eight owned hooks in ~/.codex/hooks.json, preserving unrelated hooks.

For an already provisioned board powered elsewhere, supply its exact advertised name:

```bash
python3 install.py --ble-name TrafficLight-ABCD
```

For the original wired profile use `--transport serial`. Do not use an Arduino Uno sketch as nRF52840 firmware.

Dependencies are pinned in scripts/codex_setup.py: pyserial 3.5, Bleak 0.22.3, py2app 0.28.8, setuptools below 71. Bleak installs PyObjC/CoreBluetooth dependencies. No Arduino CLI or extra CircuitPython board libraries are required for the wireless profile. The local app is an alias build and needs its runtime directory and virtual environment to remain present.

## 5. Approve the two access gates

1. Allow **Traffic Light Bridge** under macOS System Settings → Privacy & Security → Bluetooth, or accept its expected Bluetooth permission prompt. If macOS requires Touch ID/password, authenticate directly in the OS dialog.
2. Review hooks in each detected provider using its normal hook/trust workflow; see [provider setup](docs/PROVIDERS.md). For Codex use `/hooks` in the CLI. Start a fresh/resumed session after approval as needed. Writing hooks.json does not grant trust.

The repository does not modify TCC privacy databases, fabricate trust hashes, request Full Disk Access, or replace the existing Codex `notify` command.

## 6. Verify before unplugging

```bash
python3 manage_hooks.py status
python3 scripts/verify_hardware.py
```

The status must show BLE connected, a ble:// peer, and a firmware response with transport=ble and the correct GPIO values. The verification command briefly overrides the physical light for testing, then restores the tracked chat state. Have the human confirm all LEDs visibly illuminate. Test a real prompt, completion and approval request as well; synthetic signals alone do not prove hook dispatch.

Move power to a wall USB supply or an approved battery only after the BLE test. Use [battery instructions](docs/BATTERY.md), then perform [power-cycle acceptance](docs/TESTING.md).

## 7. Updates and removal

```bash
git pull --ff-only
python3 scripts/flash_nicenano.py  # USB connected, if firmware changed; reset afterwards
python3 install.py --no-hooks    # refresh host service without changing approved definitions
```

Run the full installer if hooks changed; review them again. Roll back through Git and the board backup, then reinstall the selected version. Disable using `python3 manage_hooks.py disable`. Runtime dependencies, backups, and board firmware remain; see [hook removal](HOOKS_GUIDE.md).

## Provider discovery

The default installer detects supported local tools and installs their adapters. Preview with `python3 scripts/provider_setup.py --detect`; restrict with `python3 install.py --providers codex claude`. Missing providers are not downloaded automatically. Existing disabled hooks and policies remain respected. See [provider setup and acceptance](docs/PROVIDERS.md).

## Source access and consumer packaging

This is the private maintainer/invited-tester source workflow. Cloning requires authorized GitHub access. Public customer documentation is https://github.com/alfonsoforcen3/TrafficLights_Setup. A standalone signed/notarized consumer installer has not been released yet; public documentation alone cannot install this implementation.

## Move first clawdy to another Mac

This unit is already flashed, with green on P0.09, amber on P1.11, red on P1.13 and BLE name `first clawdy`. Do not reflash or recreate its board profile when installing on another laptop. It needs power and Bluetooth proximity, not USB data.

Release it from the old Mac first, using `python3 manage_hooks.py disable` in this checkout. This disables the old Mac's traffic-light integration. Then, on the new Mac, clone this private repository with an authorized GitHub account and run:

```bash
python3 install.py --ble-name "first clawdy"
python3 manage_hooks.py status
python3 scripts/verify_hardware.py
```

Allow Traffic Light Bridge Bluetooth access in macOS and review detected provider hooks. Expect the three lights to blink together while searching, a short connection sequence, then normal tracked state. Require a connected `ble://` peer and board acknowledgements; confirm the LEDs visually. Only one Mac should control this unit at a time. New-Mac installation has not yet been tested on the user's second laptop. Battery percentage and charging are still unverified.

For release verification, agent handoff requirements, and restoration after disabling hooks, follow [the laptop handoff procedure](docs/LAPTOP_HANDOFF.md).
