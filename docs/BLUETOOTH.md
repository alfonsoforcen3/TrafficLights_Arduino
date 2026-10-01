# Bluetooth and power-cycle behavior

Commands follow this path:

```text
Codex event → traffic.py → localhost TCP bridge → CoreBluetooth/Bleak → nRF52840 GPIO
```

The board exposes the Nordic UART service `6e400001-b5a3-f393-e0a9-e50e24dcca9e`; RX ends in 0002 and TX ends in 0003. GATT writes carry a state character, and TX notifications return chunked newline-delimited JSON. A report with transport=ble proves the command reached the firmware by BLE. No routine USB serial connection is used in BLE mode.

The host stores the board's name/transport in ~/.local/share/trafficlights/connection.json and tracked sessions in sessions.json. Firmware files persist on CIRCUITPY. Powering off does not erase them. After board startup, green is the boot default; it advertises again, and the running host scans/reconnects and sends its current aggregate state. The firmware does not need to remember the previous color in flash. This avoids repeatedly writing flash for every prompt.

The bridge sends a state heartbeat every three seconds. A connection drop clears its connected status/report; it scans again and retries. Scanning/connection windows mean recovery can take seconds or longer, especially after Mac sleep, disabled Bluetooth, OS permission changes, or another central holding the connection. The login service starts after the user logs in, not before login and not while the Mac is powered off.

On helper restart, valid recent host sessions are restored from disk. Sessions older than 24 hours expire. Abruptly terminated chats can therefore leave stale amber/red; run `python3 manage_hooks.py reset` to clear abandoned sessions. That intentionally resets every tracked chat. Successful user prompt/stop hooks normally keep state current.

The locally built Mac helper uses an alias app bundle with a Bluetooth usage description; retain its virtual environment and runtime directory. Do not rebuild/delete the app casually, since changed app identity may trigger permission review. macOS permission and Codex hook trust are independent.

The current BLE service is for nearby indicator control and does not implement encrypted bonding or a physical enrollment button. It does not transmit prompts or credentials; it sends state/GPIO reports. Before commercial distribution, consider enrollment and a longer unique factory ID to prevent cross-device control or naming collisions. No unlimited uptime or battery-life guarantee has been measured.

Bluetooth operations have explicit time limits: scan 15 s, connect 20 s, notification setup 10 s, writes 5 s, and disconnect cleanup 5 s. Failed or timed-out attempts clear the connection and retry; recovery is not instantaneous. A green LED alone does not prove a live host connection.
