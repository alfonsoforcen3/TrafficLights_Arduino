# Install and activate Clawdy

This is the authorized maintainer/tester source workflow. The repository is
private; Git access is required. A signed standalone consumer installer is not
yet available. Use a stable checkout path: provider hooks point to that path.

| Host | Installation / activation | Current evidence |
| --- | --- | --- |
| Native macOS | Supported local installer and login helper | BLE hardware, OLED and Codex hook signals verified on the prototype |
| Native Windows | Implemented local installer and user Startup launcher | This revision needs native BLE, OLED, real-provider and login acceptance |
| Linux / WSL | Installer rejects this platform; no supported activation | Hardware-free tests only; see Linux section |

## Before installing

1. Power the pre-flashed board and enable Bluetooth on the laptop. Use its exact
   printed Bluetooth name. `TrafficLight-ABCD` below is a placeholder.
2. Release any other controlling laptop first with its `manage_hooks.py disable`.
   See [handoff](LAPTOP_HANDOFF.md). Do not run two companions against one unit.
3. Use native Python 3.9+ with pip/venv, Git, and a local supported AI application.
   New OS/Python combinations require acceptance; the tested Mac uses Python
   3.9.6. The installer does not install or sign into Codex, Claude, Gemini or Cursor.
4. For factory/DIY boards, confirm board identity and wiring using
   [hardware](HARDWARE.md) and [factory provisioning](../INSTALL.md). Ordinary
   pre-flashed units need no UF2/bootloader update or USB data connection.

Do not copy the original prototype's name/profile onto another board. The
OLED-equipped original unit is TrafficLight-16DE; first clawdy is a different
unit with different wiring. Moving laptops preserves the board firmware/profile.

## macOS: install and activate

Run in Terminal:

```bash
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
python3 scripts/provider_setup.py --detect
python3 install.py --ble-name "TrafficLight-ABCD"
```

The installer activates the companion immediately and installs a user login
LaunchAgent. It creates `~/.local/share/trafficlights/venv`, installs Traffic
Light Bridge and detected provider hooks, and preserves unrelated settings.
To select only certain installed providers, use
`python3 install.py --ble-name "TrafficLight-ABCD" --providers codex claude`.

Allow **Traffic Light Bridge** under System Settings → Privacy & Security →
Bluetooth if prompted. Authenticate directly in OS dialogs. Review the Traffic
Light hooks in Codex's Hooks settings or CLI `/hooks`, and Claude Code's `/hooks`.
For Gemini CLI, use its `/hooks` panel; for Cursor, inspect hooks configuration
and output. Normal workspace trust/managed policies still apply. Restart existing
provider sessions if needed. The installer cannot grant hook trust.

Use the installed Python for checks:

```bash
~/.local/share/trafficlights/venv/bin/python manage_hooks.py status
~/.local/share/trafficlights/venv/bin/python scripts/verify_hardware.py --transport ble
```

An active service alone is not proof of activation on the physical board. Require
`hardware_connected=true`, `transport=ble`, a `ble://` peer and current GPIO
acknowledgements. The verifier briefly tests lights then restores tracking;
confirm their visible colors and the OLED. Submit a real prompt, wait for its
completion, and check the light/display react after hook approval.

The service starts at user login; a login entry is not a tested reboot outcome.
The runtime log is `~/.local/share/trafficlights/bridge.log`. An optional local
dashboard is [http://127.0.0.1:8766/](http://127.0.0.1:8766/).

## Windows: install and activate

Use **native PowerShell and Windows Python**, not WSL. Install Git and Python
with pip, venv and pythonw. Keep the checkout path free of percent signs/quotes.
Enable the Windows Bluetooth adapter. The companion discovers the board directly;
there is no audio-device pairing step. Do not bypass corporate policy if Git,
dependencies, USB writes or Startup execution are blocked.

```powershell
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
py -3 scripts/provider_setup.py --detect
py -3 install.py --ble-name "TrafficLight-ABCD"
```

The installer activates the companion immediately, adds detected provider hooks,
and creates a per-user `TrafficLightBridge.vbs` in the Windows Startup folder.
This launches pythonw at login; it is not a Windows service and has no automatic
crash restart. Select providers with `--providers codex claude` if desired.
Review hooks/workspace trust inside each provider as described above.

```powershell
& "$env:USERPROFILE\.local\share\trafficlights\venv\Scripts\python.exe" manage_hooks.py status
& "$env:USERPROFILE\.local\share\trafficlights\venv\Scripts\python.exe" scripts/verify_hardware.py --transport ble
```

Require the same BLE/GPIO/visible checks as macOS. Logs are in
`$env:USERPROFILE\.local\share\trafficlights\bridge.log`. Test real provider
turns, simultaneous sessions, reconnect, and logout/login separately, recording
results with [Windows findings](windows/FINDINGS_TEMPLATE.md). This Mac run does
not certify Windows OLED or Bluetooth behavior. See the
[Windows guide](windows/INSTALL.md) for native acceptance and policy limits.

## Linux / WSL: current limit and development checks

**There is no supported Linux/WSL installation or activation path in this
revision.** `install.py` deliberately rejects them before provisioning a runtime.
Passing the Ubuntu CI jobs does not establish Linux Bluetooth, provider-hook or
startup integration. Use a native Mac or Windows companion for the physical unit.

Linux contributors can clone the source and run hardware-free checks:

```bash
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
python3 -m venv .venv
.venv/bin/python -m pip install pyserial==3.5 bleak==0.22.3
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_docs.py
```

These commands do not install hooks, start a companion or connect the board.
A future Linux implementation needs explicit installer support, a user startup
mechanism, native BLE permissions/access, and real-provider/hardware acceptance.
Do not manually run the Mac helper or present raw bridge startup as a qualified
Linux installation.

## What the OLED shows

OLED support is optional firmware on the documented 128×64 I²C prototype.
Existing LED-only units keep their profile and do not require a display.
See [wiring and per-unit configuration](HARDWARE.md) before firmware updates.

- Top left: working sessions only (`N WIP`); ready, error and input-waiting chats
  are excluded. Disconnected/unknown counts show `-- WIP`.
- Top right: the larger Clawdy title; the separator stays fixed.
- Below: animated Clawdy for working Claude Code, OpenAI mark labelled CODEX for
  working Codex, Gemini star for working Gemini CLI, neutral icon for unknown
  providers. Multiple working providers rotate every five seconds. Clawdy is the
  fallback when no provider is working or the board is disconnected.
- Status comments rotate through four funny phrase pairs every five seconds.
  Colors continue to prioritize input → error → working → ready.

Provider identity comes from local hooks, not a browser tab or the model selected
inside another app. Ordinary ChatGPT/Claude/Gemini web chats are unsupported.
Only state, working totals and provider flags reach BLE; prompts/transcripts and
session identifiers are not sent. Missed end events can leave a working record
until the existing 24-hour expiry; WIP is not an inventory of open UI windows.

## Update, disable and reactivate

Update the stable checkout with `git pull --ff-only`. If approved hooks have not
changed, refresh only the companion:

```bash
# macOS
python3 install.py --no-hooks --ble-name "TrafficLight-ABCD"
```

```powershell
# Windows
py -3 install.py --no-hooks --ble-name "TrafficLight-ABCD"
```

If hooks changed, or if you previously disabled the integration, rerun the full
installer without `--no-hooks` and review hooks. This is the activation command;
no separate enable step is needed. Do not rely on legacy `manage_hooks.py enable`
for the complete modern multi-provider/BLE setup.

Disable/release:

```bash
# macOS, from the stable checkout
~/.local/share/trafficlights/venv/bin/python manage_hooks.py disable
```

```powershell
# Windows, from the stable checkout
& "$env:USERPROFILE\.local\share\trafficlights\venv\Scripts\python.exe" manage_hooks.py disable
```

Disable removes owned hooks and login startup and stops the companion. Cached
packages, backups and firmware intentionally remain. For moving laptops, verify
the old listener/startup are absent before activating the new host; follow
[handoff](LAPTOP_HANDOFF.md). Linux has no installed integration to disable here.

For board updates, preserve hardware_config.json and existing files. Copy all
firmware dependencies before code.py using the documented provisioner; reset
if boot.py changed. Never reflash a pre-flashed unit merely to connect another OS.
See [acceptance](TESTING.md) and [troubleshooting](TROUBLESHOOTING.md). The Mac
BLE-write serialization fix passed a two-minute stress observation and the owner
reported the startup blinking had stopped; extended uptime remains unverified.
