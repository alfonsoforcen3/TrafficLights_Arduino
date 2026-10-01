# Troubleshooting

Start with `python3 manage_hooks.py status` and ~/.local/share/trafficlights/bridge.log. Hook logs are in scripts/traffic.log. Never publish raw user configs/credentials in a tester report.

| Symptom | Check/action |
| --- | --- |
| All LEDs off but GPIO reports correct | Soldered headers, common ground, LED polarity, resistor continuity, exact Nordic pin labels; software cannot see physical contact |
| Green works but prompts do not show amber | Real UserPromptSubmit entries in traffic.log; Codex hook trust; fresh session; board transport/connection/report |
| Board disconnected | Power, Mac Bluetooth, permission for Traffic Light Bridge, exact saved name, nearby/other Mac connection; allow retry time |
| Bridge says connected to wlan-debug | Wrong legacy runtime; update with install.py --no-hooks. Current code must never choose debug/Bluetooth console fallback ports |
| BLE not authorized | System Settings → Privacy & Security → Bluetooth; allow the named helper. Authenticate in OS, not chat |
| Brief Bluetooth turned-off error on startup | Allow initialization/retry; if persistent check Bluetooth toggle and permission |
| USB download never appears | Data cable, reset/bootloader sequence, exact board ID; preserve backup rather than trying random UF2 files |
| No dedicated serial response | Reset after boot.py changes; confirm data-only USB CDC port and correct firmware |
| New hooks pending trust | Review /hooks; moving repo or changing interpreter/commands changes definitions |
| Red/amber remains after a crashed chat | Close/finish chats normally or use manage_hooks.py reset to clear all sessions |
| Battery switch off but LEDs stay on | USB is still supplying power |

The helper listens only on 127.0.0.1:8765. Do not expose this port externally. If another process owns it, identify the process before stopping it. On macOS inspect `launchctl print gui/$(id -u)/local.trafficlights.bridge`; restart only that owned service using `launchctl kickstart -k gui/$(id -u)/local.trafficlights.bridge`.

A reported open device is not a board acknowledgement. Confirm firmware_report, mode, GPIO values, and transport=ble; then verify the actual visible LED.
