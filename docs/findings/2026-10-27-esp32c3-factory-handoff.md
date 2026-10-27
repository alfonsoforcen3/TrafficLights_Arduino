# ESP32-C3 factory handoff — 27 October 2026

## Unit and source

The USB-connected unit has immutable identity suffix `5D1C`; its factory label is
`Clawdy-E83DC1815D1C`. The chip identifies as ESP32-C3 QFN32 revision 0.4,
40 MHz crystal, 4 MiB embedded XMC flash. Its exact PCB supplier is unverified.
The owner confirmed the resistor-protected active-high wiring and standalone
LED test: red GPIO3, amber GPIO2, green GPIO1. This is a separate unit from
the earlier ESP32 and nRF52840 boards.

Production source: `firmware/esp32c3/`, Arduino-ESP32 3.3.2,
ArduinoJson 7.4.3, target `esp32:esp32:esp32c3:CDCOnBoot=cdc,FlashSize=4M`.
Explicit compiler flags set green=1, amber=2, red=3 and active-high=1.
The final build uses 680584 bytes of program space and 28560 bytes of RAM.
Application binary SHA-256: `a3f186fc991750bad00f0f196a61871bea1f2a44d1ffe9582901753bc4d2902c`.

## Factory USB results

- Preserved and SHA-256 verified the entire previous 4 MiB flash in a private
  local factory cache. No backup, raw logs or per-user settings are committed.
- Decoded the generated partition table, then erased only its NVS region
  (`0x9000`, size `0x5000`) before first production provisioning.
- Uploaded bootloader, partition table, boot-app data and application over USB;
  the uploader verified all four written region hashes. The final corrective
  upload retained NVS rather than erasing the test name/persistence evidence.
- Read actual USB `Q`: firmware `traffic-esp32c3-v1`, family `esp32c3`, full
  immutable identity, protocol 1, persistent rename supported and expected pins.
- Checked actual R/Y/G GPIO readbacks, B/T diagnostics and their bounded expiry
  back to mode `O` / `searching`. Green uses 12-bit duty 2048/4095 at 5 kHz.
  Applied duty is 2048 when green is on and 0 when off. This SDK's
  `ledcReadFreq` returns 0 when duty is 0; it reports 5000 when green is on.
- Rejected a wrong-device rename and malformed name. Accepted a valid temporary
  name, verified it after an explicit USB `X` software reboot, restored the
  factory name, rebooted again and verified the restored name persisted.
- Final USB report: factory name restored, mode `O`, `searching`,
  `ble_connected=false`, `advertising=true`, `ble_error=null`, `usb_error=null`.
  The owner confirmed all three production search lights blink together.
  Serial access was closed afterward; no host companion or hooks were installed.

## Defects found and corrected

The first target compile exposed a Bluedroid-only header on the C3 NimBLE SDK;
backend-specific callbacks/CCCD setup were corrected. Target compilation also
caught UUID identifiers colliding with Arduino RX/TX pin names.

The physical USB sequence reproduced a rename reply truncated after 64 bytes
while refreshing advertising. The final source defers refresh until queued
responses drain and adds a bounded USB-output recovery path that reports a
sticky delivery error. The same physical sequence subsequently passed with a
complete rename acknowledgement. Native regression scenarios cover ordering,
stall recovery, connection epochs, bounded queues and persistent naming.

The private test harness initially expected nonzero PWM frequency while green
was off; that assertion was corrected against the installed SDK implementation.
This was a harness correction, not a measured PWM failure.

## Software validation and remaining acceptance

The main-based release candidate passed all 273 hardware-free Python/native
parser regression tests in 13.093 seconds and the local documentation link
check. These tests do not establish over-air BLE or real-provider acceptance.
GitHub target-build and platform results are recorded separately by revision.

No Bluetooth scan, pairing or connection was performed on this Mac. The SDK's
advertising flag is local stack evidence, not independent radio observation.
No desktop/service, hooks, trust, privacy or startup settings were changed for
this factory unit. Existing Mac trial/integration was retained.

Two explicit software reboot/persistence checks were performed; a physical
power-removal cycle and a clean buyer-laptop installation remain pending.
On the buyer's host, require explicit device selection, BLE firmware identity,
BLE GPIO acknowledgements, visible LEDs, approved supported-provider real turns,
reconnect and laptop-restart checks. Native Windows acceptance is also pending.
This is a factory USB-programmed unit prepared for buyer enrollment, not a claim
of completed customer, radio or cross-platform acceptance.
