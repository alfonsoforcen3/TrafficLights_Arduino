# Mac BLE reconnect investigation — 2026-10-13

The owner reported repeated connection/startup LED animations after OLED changes.
The active Mac bridge log showed real repeated Bluetooth disconnect/reconnect
cycles, including bare `29` write/connection errors, independent of the deliberate
reconnections caused by firmware updates. Only one TCP bridge listener was found.

A concrete host-side race was identified: immediate hook writes and the BLE
heartbeat (now including count/provider metadata) can concurrently call
write_gatt_char on the same Nordic UART RX characteristic. The installed
Bleak 0.22.3 CoreBluetooth PeripheralDelegate.write_characteristic uses one
future per characteristic handle and deletes that entry after completion.
Overlapping writes can overwrite that future and race deletion, consistent with
the observed bare characteristic-handle error. The source was inspected locally;
reference: https://github.com/hbldh/bleak/blob/v0.22.3/bleak/backends/corebluetooth/PeripheralDelegate.py
This is evidence for a likely root cause, not a universal explanation of radio
or power failures. No claim of a board restart was established.

Added one asyncio lock shared by every write path, covering the full acknowledged
write/timeout. Connection status is checked after acquiring the lock. Cancellation
releases it. Exception type is now included in bridge error logs instead of
recording only a bare number. The lock stays on the BLE event loop. No firmware,
GPIO, brightness, OLED layout, hook definitions, or privacy/trust settings changed.
Updated the installed Mac helper with --no-hooks and the already verified unit
name TrafficLight-16DE; the service restart itself intentionally reconnects once.

Forty-nine hardware-free tests passed, including concurrent hook/metadata writes
against a single-pending-write fake backend, disconnect while awaiting the lock,
and cancellation/next-write recovery. Existing provider/parser/display tests
remain included. Whitespace checks passed. No commits were made.

Live stability observation completed: 120.2 seconds / 303 status samples,
including a 15-second burst of overlapping write requests. Zero disconnected
samples, zero searching/connected-show startup phases, and zero Bluetooth error,
scan or reconnect log events during the observation. R/Y/G/B/O hardware
acknowledgements also passed over BLE, with oled_error=null. Normal aggregate
tracking restored. Physical confirmation that the repeated blink has stopped
was provided by the owner: the repeated blinking had stopped for now. Test uses temporary hardware_test states and always resumes tracked status,
without clearing or removing user sessions. A brief run cannot certify unlimited
uptime, physical power, sleep/wake or Mac restart. Those remain untested here.
