# Clawdy customer setup agent

Use this guide when a buyer asks a **terminal-capable local AI assistant** to
configure a newly purchased, powered Clawdy on this computer. The public source
repository is not a signed consumer installer or a cloud setup service. The
assistant must have local terminal access to the buyer's computer. An ordinary
browser AI chat cannot inspect local Bluetooth advertisements or configure
local applications.

## Before running setup

First ask the buyer to confirm that the toy is powered and nearby, and ask:

- Which exact physical Clawdy is theirs? If they do not know its advertised
  name, have them identify it from the discovery list; never choose the first
  device automatically.
- What nickname do they want? Explain that naming is offered only if the
  selected firmware reports rename support; otherwise the current name stays.
- Which detected supported local AI applications may be configured? The default
  is **all detected supported applications the buyer approves**. Show the list
  and get their approval; never enable every detected app without it. The buyer
  can choose a subset or none.
- May setup create a private Python environment and download the required BLE
  packages if they are missing? Explain this before running discovery with
  `--yes`.
- Is the toy connected over USB data, and does the buyer want an optional
  USB-to-BLE identity cross-check? It is not required for power or BLE setup;
  offer it only when the supported USB port and serial number are explicitly
  selected.
- They will need to approve normal OS Bluetooth access and review each selected
  application's hook/workspace trust. No passwords should be shared in chat.

Clawdy is powered by USB; customer runtime control uses Bluetooth Low Energy
(BLE), never USB serial. A USB data cable is not required. Optional USB identity
checking is a separate, explicit check to compare the connected board with its
BLE advertisement; it must never become a runtime transport or silent fallback.

## Inventory, discovery, and setup

1. Confirm a local terminal on native macOS. Native Windows syntax is a
   candidate and remains unaccepted; Linux/WSL and browser-only AI chats are
   unsupported.
   Running `python3 install.py` with no arguments opens guided onboarding,
   including when a saved profile exists. Review the saved profile first; never
   replace it without the buyer's approval.
2. Run the read-only inventory:

   ```bash
   python3 install.py --onboard --preflight --json
   ```

   Parse the single JSON object on stdout (`version: 1`, `mode: "preflight"`);
   progress is on stderr. It reports platform/Python/dependency availability,
   detected apps and hook policy, supported/unsupported adapter inventory, any
   existing unit, and `runtime_transport: "ble"`. It does not scan Bluetooth,
   download dependencies or write files. `customer_ready` is false. Existing
   connection details must be reviewed with the buyer; never silently replace
   another unit or transport profile.
3. If the buyer opts for a USB-to-BLE identity cross-check, inspect USB metadata:

   ```bash
   python3 install.py --onboard --list-usb --json
   ```

   This reads port metadata only. It does not open a port, query firmware, scan
   Bluetooth, download dependencies or change files. If pyserial is missing,
   the inventory reports unavailable without installing it. The buyer must
   select the exact allowlisted port and USB serial number; do not identify a
   board from VID/PID or port name alone.
4. After the buyer approves possible BLE dependency setup, list candidates:

   ```bash
   python3 install.py --onboard --list-devices --json --yes
   ```

   If BLE dependencies are absent, `--yes` may create the private venv and
   download packages before scanning. Discovery is advertisement-only: it does
   not connect to a toy, exchange firmware identity, rename, install hooks, or
   configure the host. Its JSON reports `mode: "discovery"`,
   `firmware_verified: false`, `explicit_selection_required: true`,
   `device_modified: false`, `companion_or_hooks_installed: false`, and
   `customer_ready: false`. Ask the buyer to match and select their toy by its
   exact advertised name; use the address/UUID to distinguish duplicate names.
   The only supported local adapters are Codex, Claude Code, Gemini CLI and
   Cursor. Ordinary ChatGPT, Claude Desktop and Gemini web chats are not
   supported adapters; detection is inventory, not acceptance.
5. Run the interactive flow with the buyer's choices. It selects the exact
   device and asks whether to apply the plan before connecting to it. It then
   optionally issues one bounded Q query on the exact USB port selected earlier,
   checks BLE firmware identity, and compares device ID, family and name if USB
   identity was requested. A mismatch stops setup. It flashes an identification sequence on that toy,
   and asks the buyer to confirm the physical match before rename or host
   installation. Pass the buyer-approved providers explicitly with
   `--providers codex claude gemini cursor` as applicable; this avoids silently
   broadening approval. If no providers are approved, use `--no-hooks`. Provide
   `--nickname` only when the buyer requested one; use `--keep-name` otherwise.
   The flow asks before applying setup and observes normal permissions/trust
   controls.

For an agent needing machine-readable live setup, `--json` requires `--yes`, an
exact `--ble-name` (and `--device-address` for duplicate names), a naming choice
(`--nickname` or `--keep-name`), and explicit provider choices or `--no-hooks`.
If preflight shows a saved integration, first review its name/identity with the
buyer and release the old controlling toy as needed; noninteractive replacement
also requires `--replace-existing`.
For the optional USB identity cross-check, add both `--usb-port` and
`--usb-serial`, using exact values from `--list-usb`. After the final Apply
confirmation, setup opens only that selected port, issues Q, and compares its
report with the BLE device. This check cannot select the runtime transport.
Because it has no human prompt, it also requires `--identified-device` after the
buyer has independently identified that exact toy. This flag is an operator
assertion, not machine-verifiable proof. Prefer the interactive flow when the
buyer can watch and confirm the identification sequence.

The setup JSON reports phase, software installation, recovery-record path and
per-check verification, but `customer_ready` is always false. BLE/GPIO
acknowledgements do not substitute for the buyer's visible LED confirmation,
provider trust, a real prompt/completion in each approved provider, or separate
power-cycle and computer-restart checks. Stop on errors or recovery records and
inspect partial state before retrying.

## Boundaries

Never flash a shipped toy as part of ordinary customer onboarding. Do not infer
rename support from a model name, or claim ESP32-C3 customer/provider
compatibility from a USB build, upload, Q report, GPIO readback, LED test, or
protocol unit test alone. The current factory checks are not buyer-host BLE or
live-provider acceptance. Do not bypass OS privacy, trust stores, managed policy
or disabled hooks. Never ask for account passwords in chat.

One computer controls a toy at a time. Before moving it, disable the old
computer's owned integration and verify release; do not reconnect a deliberately
released computer during code-only work. Never publish local builds, customer
logs or configuration without the owner's release request.
