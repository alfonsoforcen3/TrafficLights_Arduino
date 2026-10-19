# Private firmware safety follow-up — 18 October 2026

Scoped follow-up to the Electronics/BOM review; no board, USB/BLE connection,
flash, hooks/service change, commit or publication was performed.

## Changes

- ESP32-C3 green PWM uses shared 12-bit/5 kHz constants, default duty 2048 and
  maximum 4095, including active-low inversion and the GPIO report. This avoids
  the prior 13-bit request exceeding the default 40 MHz XTAL clock capability.
- BLE transport overflow blocks further packet dispatch and requests peer
  disconnect once. Queue/parser/overflow state is released after disconnect,
  before advertising; the next peer's first Q does not require a newline.
- nRF legacy decoding accepts only documented ASCII command bytes. Invalid UTF-8
  can no longer raise during command dispatch; BLE reset remains disabled.
- [nRF rename recovery](../NRF_RENAME_RECOVERY.md) documents interrupted-first-write
  capability loss and factory-only recovery with allocation proof and complete
  backups. Unknown NVM is never automatically cleared; no erase tool was added.
- Identity timeout tests now allow 200 ms per stalled stage and a separate 3 s
  regression guard, replacing fragile 30 ms assumptions. Production timeouts and
  cancellation requirements are unchanged.

## Validation boundary

Scoped run: **29 tests passed** across `tests.test_device_identity`,
`tests.test_esp32_protocol` and `tests.test_firmware_input_safety` using the
existing isolated Python runtime. Scoped Git whitespace checks also passed.

Native tests execute the actual ESP32 parser/recovery helper and compile factory
configuration checks, including PWM defaults, endpoints and invalid bounds.
Python tests execute the actual nRF decoder and command-dispatch AST with mocked
globals. Identity tests exercise cancellation-cooperative stalled backends.

These checks do not compile the Arduino sketch or validate BLE callbacks,
FreeRTOS queue/disconnect integration, CircuitPython hardware, LED currents,
physical PWM, power-loss durability or USB-C operation. Full factory toolchain
build and assembled-unit acceptance remain mandatory before release. Existing
OLED work and the independent mascot checkout were preserved.
