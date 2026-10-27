# Agent installation and maintenance instructions

## Default entry: a buyer setting up Clawdy

When a user points an external local AI at this repository, imports/clones it for
Clawdy, or says they bought/have a new Clawdy, begin **buyer setup** rather than a
generic code tour. An explicit source-code, review, factory or maintenance request
keeps its stated scope. Do not install merely because a background process opened
a file: start with the offline preflight and obtain the buyer's confirmation.

Read docs/CUSTOMER_AGENT.md and docs/CUSTOMER_SETUP.md. First inspect the platform
and installed supported AI applications using
`python3 install.py --onboard --preflight --json` (native Windows: `py -3`). Explain that a powered/USB-connected
toy still needs its BLE connection configured. Ask the buyer to confirm the exact
toy, nickname and which detected supported AI applications to configure, offering
all supported detected apps. Unsupported apps/browser chats are reported honestly.
Never choose the first nearby device or enable unrelated/disabled hooks silently.

Use the guided `--onboard` path. Customer runtime transport is **Bluetooth Low
Energy**, even when a USB cable identifies or powers the toy. No serial fallback,
flashing, bootloader change or guessed board selection belongs in buyer setup.
Normal Bluetooth permission and each app's hook/workspace trust belong to the
buyer. Require matched firmware identity, BLE/GPIO acknowledgements, visible LEDs
and a real turn in approved providers before reporting those checks as passed.

## Project coordination

The owner uses Alex — CEO & Project Coordination as the single project contact.
For multi-area project work, route bounded assignments to the existing specialist
chats; specialists may use subagents when useful and should choose lighter models
for routine tasks. Assign file ownership to avoid concurrent edits.

The coordinating agent must collect each assigned worker's report, review its
evidence, integrate fixes and run relevant checks before sending a final response.
A dispatch or acknowledgment is not completion. Keep waiting with bounded
wait_threads calls and provide progress updates while workers are active. If a
physical/user action prevents further verification, report that specific limit
after completing independent work. Never use traffic-light hooks to force model
continuation or change application permissions; they are status observers only.

Buyer intent: treat “I bought/have a new Clawdy connected to this machine” as a
request to configure a powered, pre-flashed unit. “Connected” is not evidence of
USB data or an established Bluetooth link. Read docs/CUSTOMER_AGENT.md and
docs/CUSTOMER_SETUP.md, then use `python3 install.py --onboard` for
Bluetooth discovery and explicit selection. Optional explicit USB identity
checking is separate from BLE runtime; automatic USB discovery is not buyer setup. Do not assume rename support on already-shipped firmware.
New firmware advertises hardware family, immutable identity and rename capability.
The owner made this source repository public on 2026-10-27. Public source does
not qualify unsigned candidate bundles or automatically authorize website deployment.
No physical customer acceptance has been established by the new hardware-free tests.

Use this workflow when a user asks to install or update this repository. Do not execute installation merely because you opened the repository.

1. Read INSTALL.md, docs/COMPATIBILITY.md, and docs/HARDWARE.md. The physical profile tested here is macOS + a nice!nano-compatible nRF52840 + local Codex/Work. Never claim cross-platform installation or ordinary ChatGPT chat support.
2. Inspect OS/Python and the selected unit identity. Inspect USB volumes and INFO_UF2.TXT/boot_out.txt only for an explicitly requested factory/DIY/recovery path; customer BLE setup does not require them. For factory work, confirm physical board/wiring information. The original GPIOs are P0.10 green, P1.11 amber, P1.13 red. First clawdy uses P0.09 green (`009` reads `600` upside down); inspect its per-unit profile and never assume P0.06. Port.pin labels are not Arduino D-pin numbers. Soldered electrical connections and resistors are required.
3. If the board is shipped pre-flashed, skip provisioning and use its printed BLE name. For factory/DIY/recovery units, provision firmware using the documented official download and checksum. Preserve CURRENT.UF2 and existing CircuitPython files. Never flash this UF2 to a board with a different ID. Do not upgrade the bootloader unnecessarily.
4. For nRF factory maintenance, reset after boot.py changes. For buyer setup, discover powered BLE candidates and explicitly select the printed factory name/identity; do not copy the developer's TrafficLight-16DE name. USB power does not establish Bluetooth connectivity.
5. Preview providers with python3 scripts/provider_setup.py --detect, read docs/PROVIDERS.md, then run python3 install.py (or --providers to restrict selection). It uses ~/.local/share/trafficlights/venv, installs the Mac helper, and preserves unrelated provider hooks/settings. Review changes to ~/.codex/hooks.json. Existing hook definitions may need trust review again when paths change.
6. Explain required user actions: allow Traffic Light Bridge Bluetooth access in macOS, and review provider-specific hooks/workspace trust (Codex and Claude /hooks, Gemini /hooks panel, Cursor hook output). Never alter trust stores or macOS privacy databases to bypass these actions. Never request passwords in chat; let users authenticate directly in OS dialogs.
7. Run python3 manage_hooks.py status and python3 scripts/verify_hardware.py. A running TCP listener or open serial device is not proof of physical delivery. Require hardware_connected=true, transport=ble, a ble:// connection, and board GPIO acknowledgements with transport=ble. Ask the user to confirm visible LEDs.
8. Follow docs/TESTING.md for board reset / power-cycle / Mac restart checks. Tell the user which were actually tested. Do not promise unlimited uptime, instantaneous reconnection, or unmeasured operating endurance.

Updates: use python3 install.py --no-hooks when approved hooks need no changes. Keep the clone at a stable path; moving it changes hook paths. Disable with python3 manage_hooks.py disable; cached packages, backups and board firmware remain intentionally.

Repository work: document each working iteration and its limitations, run meaningful tests, and commit only authorized project changes. Do not add the independent claude-mascot-3d Git checkout or local logs/configuration/firmware backups. Do not auto-commit future work without user authorization.

Ruflo MCP tools may be used when available for complex tasks; they are not an installation prerequisite. If unavailable, continue with local tooling. Do not install a swarm or delegate merely to install this product.

Laptop handoff: read [docs/LAPTOP_HANDOFF.md](docs/LAPTOP_HANDOFF.md) when asked to release a unit or connect another laptop. Stop and disable the old Mac's owned integration, verify the login service and TCP listener are absent, then install on the new Mac using the exact board name. First clawdy is already flashed and named `first clawdy`; do not reflash or replace its profile for a handoff. Do not reconnect from a released Mac without explicit user authorization. Document completed handoffs and distinguish old-Mac release from unverified new-Mac connection.

Windows work: the installer selects native macOS or Windows; Windows acceptance remains revision-specific. For an explicitly requested Windows implementation/install, read docs/windows/README.md and docs/windows/AGENT_PROMPT.md. Record sanitized run evidence using docs/windows/FINDINGS_TEMPLATE.md. Do not tell a Windows user the Mac installer works, silently reflash an already flashed unit, or promote Windows compatibility without native BLE and real-provider evidence.

Native desktop installation: install.py selects macOS/Windows automatically; read docs/windows/INSTALL.md on Windows. Native Windows acceptance for this revision remains pending; distinguish reported previous hardware results from local mocked tests. Never reconnect a released laptop during code-only verification.

nRF CircuitPython firmware updates: preserve per-unit configuration, include pwm_led.py before code.py, and verify green_pwm_duty=32768 at 5 kHz for default 50% green duty. ESP32-C3 uses the separate Arduino target, explicit verified GPIO/polarity flags and 12-bit duty2048/4095 at5kHz; never apply the nRF value to it. Read docs/windows/findings/2026-10-07-mac-integration.md for latest evidence and Windows next steps. Never bypass corporate USB/network policy; firmware may be updated on an authorized personal Mac. A PWM duty is not a calibrated perceived-brightness measurement.

ESP32-C3 Super Mini LED acceptance (2026-10-26): owner confirmed the separate
USB-connected ESP32-C3 unit works with red GPIO3, amber GPIO2, green GPIO1,
active-high. Read docs/findings/2026-10-26-esp32c3-led-test.md and
firmware/esp32c3_led_test/README.md before tomorrow's installation. Complete4MiB
pre-test flash backup is private in the local cache. The standalone test is
flashed; full Bluetooth/provider firmware has NOT been accepted on this ESP32.
Owner unplugged it after success; do not reconnect it or another unit incidentally.
Do not confuse this ESP32 with either nRF board or flash a nice_nano UF2 to it.

ESP32-C3 factory unit `5D1C` (2026-10-27): production source firmware/esp32c3,
red GPIO3 / amber GPIO2 / green GPIO1, active-high, was USB-flashed with verified
region hashes after a private full-flash backup. USB diagnostics and persistent
rename across two software reboots passed; factory name is
`Clawdy-E83DC1815D1C`. Owner confirmed the production searching blink. No BLE scan,
connection, bridge or hooks were enabled on this factory Mac. Read
docs/findings/2026-10-27-esp32c3-factory-handoff.md; buyer BLE/provider acceptance
and physical power-cycle checks remain pending. Never reconnect it here as part
of code-only work or substitute another unit's evidence.

Virtual Clawdy: desktop/macos is the native menu-bar prototype in public source; read its
README and docs/VIRTUAL_CLAWDY_ACCEPTANCE.md before building or changing it.
Use isolated cached builds/tests; do not restart the user's trial incidentally.
Chat routing IDs are host-only: every renderer snapshot, including startup, must
use ParentMessage.rendererSnapshot. No default hooks/hardware/startup installation.
Windows virtual UI is a separate prototype/acceptance target from the existing
Windows physical-device bridge. Never claim native Windows UI testing on macOS.
