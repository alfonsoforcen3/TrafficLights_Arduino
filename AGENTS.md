# Agent installation and maintenance instructions

Use this workflow when a user asks to install or update this repository. Do not execute installation merely because you opened the repository.

1. Read INSTALL.md, docs/COMPATIBILITY.md, and docs/HARDWARE.md. The automated tested profile is macOS + a nice!nano-compatible nRF52840 + local Codex/Work. Never claim cross-platform installation or ordinary ChatGPT chat support.
2. Inspect OS/Python, connected volumes, INFO_UF2.TXT or boot_out.txt, and physical board/wiring information. The tested GPIOs are P0.10 green, P1.11 amber, P1.13 red. Port.pin labels are not Arduino D-pin numbers. Soldered electrical connections and resistors are required.
3. If the board is shipped pre-flashed, skip provisioning and use its printed BLE name. For factory/DIY/recovery units, provision firmware using the documented official download and checksum. Preserve CURRENT.UF2 and existing CircuitPython files. Never flash this UF2 to a board with a different ID. Do not upgrade the bootloader unnecessarily.
4. Reset the board after boot.py changes. For first BLE setup, keep exactly one provisioned board connected over USB so install.py can discover its own unique name; do not copy the developer's TrafficLight-16DE name.
5. Run python3 install.py. It uses ~/.local/share/trafficlights/venv, installs the Mac helper, and preserves unrelated Codex hooks. Review changes to ~/.codex/hooks.json. Existing hook definitions may need trust review again when paths change.
6. Explain required user actions: allow Traffic Light Bridge Bluetooth access in macOS, and review/trust Traffic light command hooks in Codex (CLI /hooks). Never alter trust stores or macOS privacy databases to bypass these actions. Never request passwords in chat; let users authenticate directly in OS dialogs.
7. Run python3 manage_hooks.py status and python3 scripts/verify_hardware.py. A running TCP listener or open serial device is not proof of physical delivery. Require hardware_connected=true, transport=ble, a ble:// connection, and board GPIO acknowledgements with transport=ble. Ask the user to confirm visible LEDs.
8. Follow docs/TESTING.md for board reset / power-cycle / Mac restart checks. Tell the user which were actually tested. Do not promise unlimited uptime, instantaneous reconnection, or battery endurance.
9. Before giving battery wiring, obtain battery voltage/chemistry and board terminal/charger identification. Use docs/BATTERY.md; never apply a battery to a GPIO or guess clone polarity/charging current.

Updates: use python3 install.py --no-hooks when approved hooks need no changes. Keep the clone at a stable path; moving it changes hook paths. Disable with python3 manage_hooks.py disable; cached packages, backups and board firmware remain intentionally.

Repository work: document each working iteration and its limitations, run meaningful tests, and commit only authorized project changes. Do not add the independent claude-mascot-3d Git checkout or local logs/configuration/firmware backups. Do not auto-commit future work without user authorization.

Ruflo MCP tools may be used when available for complex tasks; they are not an installation prerequisite. If unavailable, continue with local tooling. Do not install a swarm or delegate merely to install this product.
