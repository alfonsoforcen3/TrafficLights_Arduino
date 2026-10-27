# Native Windows installation

For the shared activation/update/removal walkthrough and OLED behavior, see
[Install and activate](../INSTALL_ACTIVATE.md). Native Windows acceptance of the
OLED/provider-icon/BLE-write revision remains pending.

Use native Windows Python 3.9 or newer (64-bit recommended), with pip and venv. WSL is not supported. Install Git to clone the repository. Keep the clone at a stable path without percent signs or quotes. No administrator privileges are required by the companion installer.

Turn off or disable the companion on the old laptop before switching laptops. Enable Bluetooth on Windows. A shipped First Clawdy already has firmware: do not reflash it or pair it as an audio device in Settings. The companion discovers its BLE advertisement directly.

In PowerShell, from the repository root:

```powershell
py -3 install.py --ble-name "first clawdy" --providers claude gemini
py -3 manage_hooks.py status
py -3 scripts/verify_hardware.py
```

For a different unit, use its printed exact BLE name. Omit `--ble-name` only when exactly one provisioned board is connected by USB for name discovery. macOS uses the same installer with `python3` instead of `py -3`.

The installer detects native Windows or macOS before creating the runtime. It installs a private virtual environment, pyserial 3.5 and (for BLE) bleak 0.22.3. Windows uses `venv\Scripts\python.exe`; macOS uses `venv/bin/python` and adds the Mac Bluetooth application dependencies. Both preserve unrelated provider configuration and detect supported providers; use `--providers claude gemini` to restrict selection. Review normal provider hook/workspace trust after installation. No ordinary browser ChatGPT integration is implied.

Windows stores runtime files under `%USERPROFILE%\.local\share\trafficlights`. A per-user `TrafficLightBridge.vbs` in the Windows Startup folder launches the hidden companion with `pythonw.exe` at login. Initial installation starts it immediately. Inspect `bridge.log` in that runtime directory if startup fails. Startup is not a Windows service and has no automatic crash restart; rerun installation if necessary. The dashboard is http://127.0.0.1:8766/ while the companion runs.

Update with `git pull` followed by the installer (`--no-hooks` preserves existing definitions). Disable with `py -3 manage_hooks.py disable`; this removes owned hooks and the Startup entry and asks the running companion to shut down. An older companion that lacks shutdown support must be closed manually before updating. Backups, cached packages and board firmware remain.

Require `hardware_connected=true`, `transport=ble`, a `ble://` connection and firmware GPIO acknowledgements, then confirm visible LEDs. Test a real provider prompt, simultaneous sessions, power cycle and Windows logout/login separately. Record actual outcomes using [FINDINGS_TEMPLATE.md](FINDINGS_TEMPLATE.md), including failures and unresolved checks. Never log prompts, passwords, credentials or private email headers.

## Evidence and limitations (2026-10-06)

The owner's Windows installation email reports Windows 11 Enterprise, First Clawdy BLE GPIO R/Y/G/B/O acknowledgements, simulated Gemini hooks, preserved Claude/Gemini configuration and repeated installation. It references branch `codex/windows-support`, commit `3f6ba3e`; neither was retrievable from this repository's remote during integration. This implementation was therefore written and tested separately, rather than merged from that report.

Local macOS hardware-free tests cover regression behavior, OS paths, quoting and Windows startup generation/removal. This implementation still needs native Windows installation, real provider prompts and logout/login acceptance. An existing Startup file does not prove reboot behavior.

## Pull this firmware/hook iteration

First Clawdy was updated and visibly verified on Mac on 2026-10-07. Windows does not need to write CIRCUITPY for this handoff. Use `git pull --ff-only`, preview with `py -3 scripts/provider_setup.py --detect`, then run the full `py -3 install.py --ble-name "first clawdy" --providers claude gemini` because Gemini hook commands changed. Review trust and restart provider sessions. See [current findings](findings/2026-10-07-mac-integration.md). Do not use `--no-hooks` to apply changed hook commands. If corporate policy blocks Git/PyPI/startup, request normal IT approval; do not disable security controls. Provide sanitized findings or a patch to the owner if push is blocked.

Provider lists in exact-label commands are examples: after detection, ask the user which supported apps to configure and pass only that approved list. Use `--onboard` for a new buyer unit; never fall back to USB runtime.
