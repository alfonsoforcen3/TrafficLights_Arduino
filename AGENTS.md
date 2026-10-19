# Agent installation and maintenance instructions

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

Customer onboarding candidate: when asked to set up a powered, pre-flashed
Clawdy, read docs/CUSTOMER_SETUP.md and use `python3 install.py --onboard` for
Bluetooth discovery and explicit selection; USB discovery is only the legacy
maintainer path. Do not assume rename support on already-shipped firmware.
New firmware advertises hardware family, immutable identity and rename capability.
Keep candidate bundles and website changes private until the owner requests release.
No physical customer acceptance has been established by the new hardware-free tests.

Use this workflow when a user asks to install or update this repository. Do not execute installation merely because you opened the repository.

1. Read INSTALL.md, docs/COMPATIBILITY.md, and docs/HARDWARE.md. The physical profile tested here is macOS + a nice!nano-compatible nRF52840 + local Codex/Work. Never claim cross-platform installation or ordinary ChatGPT chat support.
2. Inspect OS/Python, connected volumes, INFO_UF2.TXT or boot_out.txt, and physical board/wiring information. The original GPIOs are P0.10 green, P1.11 amber, P1.13 red. First clawdy uses P0.09 green (`009` reads `600` upside down); inspect its per-unit profile and never assume P0.06. Port.pin labels are not Arduino D-pin numbers. Soldered electrical connections and resistors are required.
3. If the board is shipped pre-flashed, skip provisioning and use its printed BLE name. For factory/DIY/recovery units, provision firmware using the documented official download and checksum. Preserve CURRENT.UF2 and existing CircuitPython files. Never flash this UF2 to a board with a different ID. Do not upgrade the bootloader unnecessarily.
4. Reset the board after boot.py changes. For first BLE setup, keep exactly one provisioned board connected over USB so install.py can discover its own unique name; do not copy the developer's TrafficLight-16DE name.
5. Preview providers with python3 scripts/provider_setup.py --detect, read docs/PROVIDERS.md, then run python3 install.py (or --providers to restrict selection). It uses ~/.local/share/trafficlights/venv, installs the Mac helper, and preserves unrelated provider hooks/settings. Review changes to ~/.codex/hooks.json. Existing hook definitions may need trust review again when paths change.
6. Explain required user actions: allow Traffic Light Bridge Bluetooth access in macOS, and review provider-specific hooks/workspace trust (Codex and Claude /hooks, Gemini /hooks panel, Cursor hook output). Never alter trust stores or macOS privacy databases to bypass these actions. Never request passwords in chat; let users authenticate directly in OS dialogs.
7. Run python3 manage_hooks.py status and python3 scripts/verify_hardware.py. A running TCP listener or open serial device is not proof of physical delivery. Require hardware_connected=true, transport=ble, a ble:// connection, and board GPIO acknowledgements with transport=ble. Ask the user to confirm visible LEDs.
8. Follow docs/TESTING.md for board reset / power-cycle / Mac restart checks. Tell the user which were actually tested. Do not promise unlimited uptime, instantaneous reconnection, or battery endurance.
9. Before giving battery wiring, obtain battery voltage/chemistry and board terminal/charger identification. Use docs/BATTERY.md; never apply a battery to a GPIO or guess clone polarity/charging current.

Updates: use python3 install.py --no-hooks when approved hooks need no changes. Keep the clone at a stable path; moving it changes hook paths. Disable with python3 manage_hooks.py disable; cached packages, backups and board firmware remain intentionally.

Repository work: document each working iteration and its limitations, run meaningful tests, and commit only authorized project changes. Do not add the independent claude-mascot-3d Git checkout or local logs/configuration/firmware backups. Do not auto-commit future work without user authorization.

Ruflo MCP tools may be used when available for complex tasks; they are not an installation prerequisite. If unavailable, continue with local tooling. Do not install a swarm or delegate merely to install this product.

Laptop handoff: read [docs/LAPTOP_HANDOFF.md](docs/LAPTOP_HANDOFF.md) when asked to release a unit or connect another laptop. Stop and disable the old Mac's owned integration, verify the login service and TCP listener are absent, then install on the new Mac using the exact board name. First clawdy is already flashed and named `first clawdy`; do not reflash or replace its profile for a handoff. Do not reconnect from a released Mac without explicit user authorization. Document completed handoffs and distinguish old-Mac release from unverified new-Mac connection.

Windows work: the installer selects native macOS or Windows; Windows acceptance remains revision-specific. For an explicitly requested Windows implementation/install, read docs/windows/README.md and docs/windows/AGENT_PROMPT.md. Record sanitized run evidence using docs/windows/FINDINGS_TEMPLATE.md. Do not tell a Windows user the Mac installer works, silently reflash an already flashed unit, or promote Windows compatibility without native BLE and real-provider evidence.

Native desktop installation: install.py selects macOS/Windows automatically; read docs/windows/INSTALL.md on Windows. Native Windows acceptance for this revision remains pending; distinguish reported previous hardware results from local mocked tests. Never reconnect a released laptop during code-only verification.

Firmware updates: preserve per-unit configuration, include pwm_led.py before code.py, and verify green_pwm_duty=32768 at 5 kHz for default 50% green duty. Read docs/windows/findings/2026-10-07-mac-integration.md for latest evidence and Windows next steps. Never bypass corporate USB/network policy; firmware may be updated on an authorized personal Mac. A PWM duty is not a calibrated perceived-brightness measurement.
