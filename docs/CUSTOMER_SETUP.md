# Set up your Clawdy

**Public source setup; no signed standalone installer or prebuilt customer download.**
Run the setup assistant from a local checkout. The repository being public does
not mean this source build is a qualified consumer release.

## Before you begin

Power your assembled, pre-flashed Clawdy through its USB power connection.
USB supplies power; the laptop communicates with the toy over Bluetooth Low
Energy (BLE). Ordinary setup does not require a USB data connection to the
laptop. Turn on laptop Bluetooth and keep the toy nearby. The ESP32-C3 factory firmware on unit `5D1C` has passed USB identity/GPIO
checks, bounded LED diagnostics and saved-name checks across two software
reboots. The owner confirmed its production search blink. Buyer-host BLE and
real-provider acceptance remain pending; these factory USB checks do not
establish customer readiness. See the [factory record](findings/2026-10-27-esp32c3-factory-handoff.md).
Release any old controlling laptop before setup. Bluetooth is proximity-based,
not Wi-Fi; nearby units can share a room but each needs a unique name and only
one controlling laptop at a time.

Use the local terminal on native macOS or Windows, Python 3.9+, and internet for
Python packages. The public repository is
<https://github.com/alfonsoforcen3/TrafficLights_Arduino>. Clone it into a
stable local folder before asking the local assistant to follow `AGENTS.md`.
The tested Mac prototype is a different nRF52840 unit; that history does not
establish ESP32-C3 customer/provider acceptance. Clean-customer
onboarding remains pending. Native Windows onboarding acceptance also remains
pending, including its `py -3` command. Linux/WSL and ordinary browser AI
conversations are unsupported. No AI API key is required by the companion.

Use a public source checkout or an owner-supplied local build in a permanent
folder such as `~/Clawdy` or `C:\Users\YOU\Clawdy`. There is no released
prebuilt customer archive. Keep the checkout in place for updates/recovery; avoid
moving it after setup because hook paths may refer to it.

To create a checkout on macOS:

```bash
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
```

Then ask a terminal-capable local assistant in that checkout to follow
`AGENTS.md`. Use native PowerShell and `py -3` for Windows only as an unaccepted
candidate; do not claim Windows setup is verified.

## Ask a local AI assistant to set it up

A buyer can tell a terminal-capable local AI assistant:

> I have a new Clawdy powered by USB and near this computer. Before changing
> anything, ask me to identify the exact toy, choose a nickname, approve which
> detected AI apps to configure, and approve any package downloads. Use BLE for
> control; default to all detected supported local apps I approve. Follow
> `AGENTS.md` and walk me through Bluetooth and app trust approvals. Ask whether
> I want an optional USB-to-BLE identity cross-check if the toy is data-connected.

The assistant needs access to this computer's terminal and local checkout. An
ordinary browser AI conversation cannot access local Bluetooth, select the toy,
or change local app settings. For a first setup, the guided command is:

```bash
python3 install.py --onboard
```

On native Windows the candidate command is `py -3 install.py --onboard`; its
native onboarding acceptance is still pending. Do not present it as verified.
The no-argument invocation (`python3 install.py`) opens guided onboarding,
including when a saved profile exists. It displays the existing device and asks
before replacement; use explicit maintainer flags for a direct update instead.

### Local-AI inventory and device discovery

Agents can begin with a strict read-only local inventory:

```bash
python3 install.py --onboard --preflight --json
```

It emits one JSON object on stdout (`version: 1`, `mode: "preflight"`); progress
is on stderr. It reports platform/Python/dependency availability, detected
apps and hook-policy preflight, supported/unsupported adapter inventory, any
saved unit (`existing_unit`), provider selection requirement and
`runtime_transport: "ble"`. It does not scan Bluetooth, download dependencies,
or write files. Its `customer_ready` field is always `false`. Review any saved
device and transport with the buyer before replacement; never switch devices
silently. Noninteractive replacement also requires `--replace-existing` after
this review.

### Optional USB identity cross-check

USB data is not required. If the buyer wants to compare a USB-connected board
with its BLE advertisement, first list USB metadata:

```bash
python3 install.py --onboard --list-usb --json
```

This does not open a port, query firmware, scan BLE, download packages or change
files. JSON reports `mode: "usb_inventory"`, `ports_opened: false`,
`bluetooth_scanned: false`, `mutations: false`, `runtime_transport: "ble"` and
`customer_ready: false`. If pyserial is unavailable, the inventory reports that
without installing it. Only an explicitly selected, allowlisted interface with
its exact nonempty USB serial number may be queried later. The current allowlist
includes Espressif USB Serial/JTAG `303A:1001` as a candidate interface; that
identifier does not establish the exact board model or firmware.

After the buyer powers the toy and approves needed package setup, list nearby
BLE UART advertisements. Discovery is separate from runtime control:

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
names. Never choose the first candidate automatically. The only supported local
adapters are Codex, Claude Code, Gemini CLI and Cursor; ordinary ChatGPT, Claude
Desktop and Gemini web chats are unsupported. Detection does not prove live
compatibility. For `--yes` setup, explicitly pass the buyer-approved
`--providers ...` or `--no-hooks`; detecting an app never authorizes its hooks.

Prefer interactive setup after the buyer makes their choices. The wizard shows
the detected supported local apps; Enter selects all detected apps, and the
buyer can explicitly select a subset or none. Ask for and confirm the buyer's
approval before proceeding. The wizard lets the buyer select the physical unit,
confirms it with a red/amber/green sequence on that toy, then checks firmware
identity/capability before offering naming. It installs only the explicitly
approved providers. Generic Bluetooth devices are not supported. USB remains
the power source; the intended customer transport is BLE.

For the optional cross-check, pass `--usb-port` and `--usb-serial` using the
exact values selected from `--list-usb`. After the buyer confirms Apply, setup
opens only that port for a bounded Q query, then compares immutable device ID,
hardware family and BLE name with the selected BLE report. A mismatch stops
before LED identification, rename or host installation. USB is never used for
ongoing control, and setup does not fall back between transports.

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
not install firmware onto arbitrary Bluetooth boards. One ESP32-C3 unit now has
a factory-built and USB-flashed BLE candidate with initial USB Q/GPIO checks.
Rename persistence, reboot, visual LED, buyer-host BLE and provider checks
remain open before shipment.

For an offline plan preview (no scan, downloads or changes):

```bash
python3 install.py --onboard --dry-run --ble-name "EXACT LABEL" --nickname Pip --providers codex
```

For noninteractive JSON setup, `--yes` accepts installation changes but cannot
assert physical identity. Pass the exact selected `--ble-name`, `--nickname` or
`--keep-name`, and explicitly approved `--providers` (or `--no-hooks`); `--yes`
never means “enable all detected apps.” If preflight showed an existing unit,
review it with the buyer and pass `--replace-existing` only with approval. If names collide,
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
Do not claim live provider support from detection or software checks alone.
Verify an actual turn in every buyer-approved app on the customer's computer;
real-provider acceptance for ESP32-C3 remains unestablished.

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
