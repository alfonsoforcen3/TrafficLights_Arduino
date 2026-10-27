# Set up your Clawdy

**Public source setup; no signed standalone installer or prebuilt customer download.**
Run the setup assistant from a local checkout. The repository being public does
not mean this source build is a qualified consumer release.

## Before you begin

Power your assembled, pre-flashed Clawdy through its USB power connection.
USB supplies power; the laptop communicates with the toy over Bluetooth Low
Energy (BLE). Ordinary setup does not require a USB data connection to the
laptop. The searching LEDs blink together until a host connects. Turn on laptop
Bluetooth and keep the toy nearby.
Release any old controlling laptop before setup. Bluetooth is proximity-based,
not Wi-Fi; nearby units can share a room but each needs a unique name and only
one controlling laptop at a time.

Use the local terminal on native macOS or Windows, Python 3.9+, and internet for
Python packages. Mac BLE/Codex prototype operation has been physically verified;
clean-customer onboarding remains pending. Native Windows onboarding acceptance
also remains pending, including its `py -3` command. Linux/WSL and ordinary
browser AI conversations are unsupported. No AI API key is required by the
companion.

Use a public source checkout or an owner-supplied local build in a permanent
folder such as `~/Clawdy` or `C:\Users\YOU\Clawdy`. There is no released
prebuilt customer archive. Keep the checkout in place for updates/recovery; avoid
moving it after setup because hook paths may refer to it.

## Ask a local AI assistant to set it up

A buyer can tell a terminal-capable local AI assistant:

> I have a new Clawdy powered by USB and near this computer. Please set it up by following `AGENTS.md`.

The assistant needs access to this computer's terminal and local checkout. An
ordinary browser AI conversation cannot access local Bluetooth, select the toy,
or change local app settings. For a first setup, the guided command is:

```bash
python3 install.py --onboard
```

On native Windows the candidate command is `py -3 install.py --onboard`; its
native onboarding acceptance is still pending. Do not present it as verified.
The first-run invocation with no arguments (`python3 install.py`) also opens the
guided onboarding flow when no saved connection exists. Existing installations
continue their prior install/update path; use `--onboard` to explicitly enter
onboarding.

### Local-AI inventory and device discovery

Agents can begin with a strict read-only local inventory:

```bash
python3 install.py --onboard --preflight --json
```

It emits one JSON object on stdout (`version: 1`, `mode: "preflight"`); progress
is on stderr. It reports platform/Python/dependency availability, detected
providers and hook-policy preflight, and saved connection state. It does not
scan Bluetooth, download dependencies, or write files. Its `customer_ready`
field is always `false`.

After the buyer powers the toy and approves needed package setup, list nearby
UART advertisements:

```bash
python3 install.py --onboard --list-devices --json --yes
```

If BLE dependencies are missing, `--yes` permits creation/preparation of the
private venv and package downloads before scanning. The scan reports candidates
only; it does not connect, exchange firmware identity, rename, install hooks,
or configure the host. JSON uses `mode: "discovery"`,
`firmware_verified: false`, `explicit_selection_required: true`, and
`customer_ready: false`. Ask the buyer to identify the exact physical toy and
select its advertised name; use `--device-address` to distinguish duplicate
names. Never choose the first candidate automatically.

Prefer interactive setup after the buyer identifies the device. The wizard
confirms the selection with a red/amber/green sequence on that physical unit and
requires the buyer to verify it. It then checks firmware identity/capability,
offers naming only when supported, and installs the selected local provider
hooks. Generic Bluetooth devices are not supported.

If the selected firmware reports rename support, you may choose a nickname. The
wizard combines a shortened laptop name, nickname and an eight-hex device suffix
within Bluetooth's 29-byte name budget. Long names are shortened; the full
hardware identity is saved separately. Older firmware keeps its current label
and uses `--keep-name`:

```bash
python3 install.py --onboard --ble-name "EXACT LABEL" --keep-name
```

Wireless rename requires firmware that advertises rename capability. Older
firmware can keep its current name. Do not flash a nice!nano image onto an ESP32
or guess GPIO wiring. The host recognizes supported firmware protocols; it does
not install firmware onto arbitrary Bluetooth boards. ESP32-C3 candidate hardware
requires separate factory compilation/provisioning and physical qualification
before shipment.

For an offline plan preview (no scan, downloads or changes):

```bash
python3 install.py --onboard --dry-run --ble-name "EXACT LABEL" --nickname Pip --providers codex
```

For noninteractive JSON setup, `--yes` accepts installation changes but cannot
assert physical identity. Pass the exact selected `--ble-name`, `--nickname` or
`--keep-name`, and selected `--providers` (or `--no-hooks`). If names collide,
also pass the buyer-selected `--device-address`. Because JSON setup has no human
confirmation prompt, `--identified-device` is required after the buyer has
independently identified that exact physical toy; it is an operator assertion,
not machine verification. Example:

```bash
python3 install.py --onboard --json --yes --ble-name "EXACT LABEL" \
  --keep-name --providers codex --identified-device
```

Machine-readable output is one JSON object on stdout; progress is on stderr.
The final setup result reports `software_installed`, phase, recovery record and
per-check verification. `customer_ready` is always `false`: physical LED
confirmation, provider hook/workspace trust, real-provider turns, and restart /
power-cycle acceptance remain separate checks. A nonzero exit or recovery
record may indicate partial setup; inspect it and existing companion state
before retrying. `--skip-verification` leaves hardware checks pending and does
not establish acceptance.

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

Before declaring a unit ready, test USB-power disconnect/reconnect, Bluetooth
toggle, sleep/wake, logout/login, reboot and removal/reinstall separately. Record
failures and actual reconnect times. These tests do not establish unlimited
uptime.
