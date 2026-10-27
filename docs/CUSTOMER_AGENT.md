# Clawdy customer setup agent

Use this guide when a buyer asks a **terminal-capable local AI assistant** to
set up a newly purchased Clawdy on the same computer. The repository is public,
but this is still a source-based candidate: there is no signed standalone
installer or automatic cloud setup. The assistant needs local terminal access
to the buyer's computer. An ordinary browser AI chat cannot scan local Bluetooth
or configure this machine's apps.

When the buyer says, for example, “I have a new Clawdy powered and near this
computer; please set it up,” follow these steps:

1. Confirm the assistant is operating on the buyer's native Mac. Native
   Windows syntax is a candidate and Windows onboarding remains unaccepted.
   Linux/WSL and ordinary browser conversations are unsupported.
2. Start with the read-only inventory. It checks the local platform, Python,
   provider discovery/policy and saved connection status. It does not scan
   Bluetooth, download dependencies, or write files:

   ```bash
   python3 install.py --onboard --preflight --json
   ```

   Parse the single JSON object on stdout (`version: 1`, `mode: "preflight"`).
   Treat progress/diagnostics as stderr. A preflight result never means the toy
   is connected or ready.

3. Once the buyer has powered the toy and approved any needed dependency
   bootstrap, list nearby UART advertisements:

   ```bash
   python3 install.py --onboard --list-devices --json --yes
   ```

   `--yes` permits dependency setup if BLE packages are missing; that can create
   the private venv and download packages. The scan only lists advertisement
   candidates. It does not connect to a toy, exchange identity, rename, install
   hooks, or configure the host. The JSON (`mode: "discovery"`) explicitly says
   firmware is unverified and a human selection is required. Never choose the
   first candidate. Ask the buyer to identify the intended physical toy and
   choose its exact advertised name; use its address/UUID if names collide.

4. Prefer running the setup interactively so the buyer can watch the selected
   toy's red/amber/green identification sequence and confirm it. If an
   explicitly authorized noninteractive JSON setup is needed, pass the exact
   buyer-selected `--ble-name`, `--device-address` when needed, `--yes`, and
   either `--nickname` or `--keep-name`, plus the chosen `--providers` (or
   `--no-hooks`). Add `--identified-device` only after the buyer has already
   physically identified that exact unit. It is an operator assertion, not an
   automated physical check. Example:

   ```bash
   python3 install.py --onboard --json --yes --ble-name "EXACT LABEL" \
     --keep-name --providers codex --identified-device
   ```

   Setup JSON on stdout reports software installation and per-check states;
   progress goes to stderr. `customer_ready` is always `false`. Even when BLE
   and GPIO acknowledgements pass, visible LED confirmation, provider trust and
   real-provider turns remain human/customer acceptance gates. A nonzero exit
   or a recovery record means inspect the reported partial state before retry.

5. Clawdy is USB-powered. USB supplies power; normal communication with the
   computer is over Bluetooth Low Energy (BLE). USB data is not required for
   ordinary customer setup. Ask the buyer to power the toy and enable Bluetooth.
6. Allow normal operating-system Bluetooth permissions and provider hook/workspace
   trust. Never bypass privacy databases, trust stores, managed policy, or user-
   disabled hooks. Do not request passwords in chat.
7. If offered, request a nickname only when the selected firmware reports rename
   capability. Otherwise keep the existing name. Never flash a shipped toy or
   assume an older unit can be renamed.
8. Verify BLE firmware acknowledgements and ask the buyer to confirm the LEDs
   visibly change. Run a real turn in each selected, configured local provider;
   synthetic tests are not real-provider acceptance.
9. Explain that one computer controls a toy at a time. Before moving it, disable
   the old computer's owned integration and verify it is released. Do not
   reconnect an intentionally released computer during code-only work.

The setup assistant handles the software steps it can access, but it cannot
approve OS permissions, select a physical unit, grant provider trust, or observe
LEDs on the buyer's behalf. No AI API key is needed by the Clawdy companion.
Never publish a local build or customer logs/configuration without the owner's
release request.
