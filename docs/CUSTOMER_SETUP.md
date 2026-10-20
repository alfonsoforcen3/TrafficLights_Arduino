# Set up your Clawdy

**Private review candidate. Not yet a public customer download.** This source
bundle runs a terminal setup assistant; it is not a signed standalone installer.

## Before you begin

Power your assembled, pre-flashed Clawdy from its approved USB power source.
It does not need a USB data connection to your laptop. The searching LEDs blink
together until a host connects. Turn on laptop Bluetooth and keep the toy nearby.
Release any old controlling laptop before setup. Bluetooth is proximity-based,
not Wi-Fi; nearby units can share a room but each needs a unique name and only
one controlling laptop at a time.

Use native macOS or Windows with Python 3.9+ and internet for Python packages.
Mac BLE/Codex prototype operation has been physically verified; this new setup
flow still needs clean-customer acceptance. Native Windows acceptance remains
pending. Linux/WSL and ordinary AI browser conversations are unsupported.
No AI API key is required for the light companion.

Extract the approved bundle to a permanent folder such as `~/Clawdy` or
`C:\Users\YOU\Clawdy`. Do not run from Downloads and move/delete it afterward:
new provider hooks run a copy from `~/.local/share/trafficlights/traffic.py`.
Keep the extracted folder for updates/recovery; avoid running legacy hooks
directly from cloud-backed Desktop or Downloads files.

## Terminal setup

Open a terminal in the extracted `Clawdy` folder:

```bash
python3 install.py --onboard
```

On Windows use `py -3 install.py --onboard` if `python3` is unavailable.

The assistant previews installed local AI apps, asks which hooks to configure,
creates an isolated Python environment if needed, scans nearby compatible UART
devices, and requires you to select your toy. It checks actual Clawdy firmware
before attempting to configure it. Generic Bluetooth devices are not supported.

Choose a nickname. The advertisement combines a shortened laptop name, your
nickname and an eight-hex device suffix, within Bluetooth's 29-byte name budget.
Long names are shortened; the full hardware identity is saved separately.
An older toy without rename support can be installed with its current label:

```bash
python3 install.py --onboard --ble-name "EXACT LABEL" --keep-name
```

Wireless rename needs the new factory firmware. Do not flash a nice!nano image
onto an ESP32, or guess GPIO wiring. The host recognizes supported firmware
protocols; it does not install firmware onto arbitrary Bluetooth boards.
ESP32-C3 candidate hardware requires separate factory compilation/provisioning
and physical qualification before shipment. No battery/charging qualification
is implied by a successful connection.

For an agent-assisted offline preview (no scan, downloads or changes):

```bash
python3 install.py --onboard --dry-run --ble-name "EXACT LABEL" --nickname Pip --providers codex
```

For a previously selected and physically identified unit, `--yes --identified-device
--ble-name "EXACT LABEL" --nickname Pip --providers codex` accepts the displayed
changes. `--yes` alone never claims a physical observation. Use `--device-address` if names
collide, using the identifier shown by discovery. Confirm the intended physical
toy before any automated invocation. `--no-hooks` configures only the companion.
The interactive flow displays a red/amber/green identification sequence before
renaming and asks you to confirm the selected toy. After installing, it checks
actual BLE status, cycles the lights, and asks for visible confirmation.
`--skip-verification` leaves these checks explicitly pending; it is not acceptance.

## Permissions and verification

Approve the normal Bluetooth request for the scanning terminal/Python process
if macOS requests it, then allow **Traffic Light Bridge** for the installed helper.
If discovery is denied, review System Settings → Privacy & Security → Bluetooth
and retry. Authenticate only in normal OS dialogs. On Windows check Bluetooth
adapter permissions/policy. No privacy or trust bypass is part of setup.

Review hooks in your actual local application: Codex `/hooks`, Claude Code
`/hooks` and workspace trust, Gemini CLI `/hooks` panel, Cursor hooks/output.
Detection is an inventory, not proof that a version is compatible or signed in.
Claude/Gemini/Cursor adapters have software coverage; real-provider acceptance
is still pending. Their underlying AI model does not affect adapter selection.

```bash
python3 manage_hooks.py status
python3 scripts/verify_hardware.py --transport ble
```

Require `hardware_connected=true`, `transport=ble`, a `ble://` connection and
current board GPIO acknowledgements. Confirm each LED visibly illuminates.
Then submit and finish a real prompt in every selected provider. Test two chats
at once: finishing one must leave amber while the other works. A running helper
or synthetic signal alone is not success.

## Move, troubleshoot, remove

If the toy is absent, check power, range, permissions and competing laptops.
Duplicate names are refused. Firmware identity mismatch requires reenrolling
the intended toy, not bypassing the check. Review any disabled provider policy
yourself; the assistant leaves those settings unchanged. Setup backs up changed
provider files and preserves unrelated hooks. An interrupted install may leave
some installed components; rerun after resolving the reported error.

The wizard writes a private per-unit recovery record under
`~/.local/share/trafficlights/onboarding/` before requesting a rename or starting
installation. It records the previous/target names, selected providers and last
setup phase, not AI prompts. This is a checkpoint and retry aid, not an automatic
rollback or an automatic resume. If a rename acknowledgement is lost, look for
either name and physically identify the intended toy again. If installation
fails after renaming, use the confirmed new name with `--keep-name` on retry.
Check for a still-running installer and inspect existing companion status first;
timing out the direct installer cannot guarantee all child processes stopped.
Do not run concurrent setup sessions against the same laptop/runtime.

EOF or Ctrl-C stops further wizard actions with a concise cancellation message.
Already saved device names, dependencies or partially installed services/hooks
can remain. A completed installation still needs the Bluetooth/visible LED and
real-provider checks below; a recovery record is not proof of acceptance.

For an existing installation whose hooks point into a cloud-backed checkout,
preview `python3 scripts/migrate_hook_runtime.py --dry-run`, then use `--apply`
to update only existing owned commands and copy the observer into the runtime.
This creates backups, preserves disabled/unrelated settings and does not start
the service or enable hooks. Review the changed command paths in the providers'
normal hook trust controls. No trust database changes are performed.

Before changing laptops or removing the integration:

```bash
python3 manage_hooks.py disable
```

This removes owned provider hooks and startup integration; cached dependencies,
backups and board firmware remain. Stop the old laptop before connecting the
new one. After a rename, update other approved hosts deliberately; do not have
two hosts competing for a toy. Automatic startup runs at user login.

Before declaring a unit ready, also test external-power off/on, Bluetooth
toggle, sleep/wake, logout/login, reboot and removal/reinstall. Record failures
and actual reconnect times. No unlimited uptime or battery endurance is promised.
