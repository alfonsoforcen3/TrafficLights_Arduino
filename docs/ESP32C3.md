# ESP32-C3 engineering candidate — not a qualified shipping profile

The `firmware/esp32c3/` source is a development candidate for the explicitly
identified ESP32-C3 unit. It does not replace the tested nRF52840 firmware. USB
evidence exists for a separate LED diagnostic on two units, including the
current USB unit with MAC suffix `5D1C`; that does not qualify the full BLE
firmware, customer onboarding, or provider integration. The precise PCB vendor
and board revision beyond the reported ESP32-C3 module identity remain unknown.

## Standalone LED diagnostic accepted on two units — 26/27 October 2026

A separate [cable-only diagnostic](../firmware/esp32c3_led_test/README.md) was
compiled, uploaded and physically confirmed on the owner's ESP32-C3 Super Mini:
red GPIO3, amber GPIO2, green GPIO1, active-high. All five test phases were also
verified by USB GPIO readback. See the [test evidence](findings/2026-10-26-esp32c3-led-test.md).
This acceptance applies to that diagnostic and the identified unit only. A
second, distinct unit (`5D1C`) passed the same five-phase USB diagnostic on
27 October; see [the recorded test](findings/2026-10-26-esp32c3-led-test.md).
The USB LED test is not evidence of BLE connectivity, USB factory firmware
acceptance, or customer/provider setup.

## Factory inputs and build boundary

Factory must identify the exact board/module and supplier schematic, USB/power
circuit, boot/strapping/flash pins, soldered LED GPIOs, LED polarity and series
resistors before building. Nordic P0/P1 labels are not ESP GPIO numbers. Define
`CLAWDY_GREEN_GPIO`, `CLAWDY_AMBER_GPIO`, `CLAWDY_RED_GPIO` and
`CLAWDY_ACTIVE_HIGH` using that verified factory profile. `factory_config.h`
deliberately emits a compiler error while these inputs are missing and rejects
duplicate pins. Runtime checks reject GPIOs unavailable for output, but cannot
detect a pin reserved by a particular board's flash, USB, boot or wiring.

The first full-target attempt with Arduino-ESP32 3.3.2 stopped because the C3
target lacks the Bluedroid header `esp_gap_ble_api.h`; the target uses NimBLE.
After porting, the full target compiled with Arduino-ESP32 3.3.2 and ArduinoJson
7.4.3 (680,584 bytes flash, 28,560 bytes static RAM) and was uploaded over USB;
all four written regions passed hash verification. This establishes the factory
build and upload on unit `5D1C`, not customer BLE acceptance. Supply verified
GPIO/polarity macros through factory build flags or an approved board-specific
profile. There is intentionally no generic ready-to-flash binary or guessed-pin
upload command. USB firmware provisioning belongs to factory/service workflows,
with the correct board and prior data/configuration preserved. Customers receive
pre-flashed units; USB powers Clawdy while customer control is intended to use
BLE and does not require a computer USB data connection. Do not treat USB serial
as the normal customer control transport.

Green uses 5 kHz **12-bit** PWM, default duty 2048 of 4095, configurable with
`CLAWDY_GREEN_DUTY`. This is approximately 50% electrical duty, not calibrated
brightness. Its GPIO report declares the resolution; do not require the nRF52840
16-bit duty 32768 on this different peripheral. Red/amber use digital outputs.
The 12-bit configuration fits the default 40 MHz XTAL LEDC source; 13 bits at
5 kHz would require a faster source and could fail before BLE startup. Frequency
and duty still require measurement on the actual board/toolchain.

## Source-level host protocol and first USB Q report

The candidate exposes the same Nordic UART UUIDs as the nRF52840 profile:
service `6e400001-b5a3-f393-e0a9-e50e24dcca9e`, RX `...0002...`, TX `...0003...`.
The primary advertisement includes the service; the scan response includes the
full name. RX accepts write/write-without-response; TX sends newline-delimited
JSON in at most 20-byte notification fragments.

Commands G/Y/R/B/O, Q and T are supported. X restarts only when received
over local USB serial; BLE X is ignored. `N<count>\n` and `P<mask>\n` metadata
track 0–9999 working sessions and provider bits 0–15, without transcripts or
session IDs. Metadata is cleared on disconnect. There is no OLED renderer in
this candidate.

Transport queue overflow or an oversized incoming BLE write latches input off
and requests disconnect of the current peer. The latch, parser and old queue are
cleared only after release, before advertising again. Recovery requires a fresh
connection; it does not wait indefinitely for a newline that legacy Q/colour
commands never send. A report interrupted by overflow may be incomplete and must
not be treated as acknowledged. A malformed/oversized identity frame within an
otherwise intact transport is still consumed through its terminating newline.

The first USB serial Q report from unit `5D1C` returned
`firmware=traffic-esp32c3-v1`,
`hardware_family=esp32c3`, `device_id` as the full uppercase eFuse base-MAC hex
string, `identity_protocol=1`, and `rename_supported` only after the Preferences
namespace opens. Its default name is `Clawdy-<full-device-id>`. GPIO keys are
explicit `GPIO<number>` names with `green_pin`, `amber_pin`, `red_pin`, boolean
commanded state, PWM details, mode, display phase, count and provider mask.
The observed report identified the unit by suffix `5D1C`, reported name
`Clawdy-E83DC1815D1C`, `identity_protocol=1`, `rename_supported=true`,
`ble_connected=false`, advertising active, no BLE error, searching mode `O`,
and GPIO mapping green 1 / amber 2 / red 3. Green PWM reported 12-bit,
2048/4095, 5 kHz while on. These fields match the host's dynamic GPIO
verification rather than claiming nRF pin labels. Rename persistence and
post-reboot identity have not yet been confirmed.

The source's persistent rename path accepts a fragmented frame bounded to 192
UTF-8 bytes:

```text
!{"op":"rename","name":"Laptop-Pet-1234ABCD","device_id":"FULLUPPERHEXMAC"}\n
```

Here `\n` denotes one newline byte. The exact immutable device ID is required;
names accept 1–29 UTF-8 bytes, no ASCII controls or invalid UTF-8. Identity and
metadata frames are consumed before legacy colour commands, including malformed
or oversized payloads. Preferences stores only `clawdy/ble_name`, preserving
other namespaces. The intended success path requires persistent write and
readback before the newline JSON acknowledgement containing
`identity_ack=rename`, `ok=true`, `persistent=true`, device ID and the new BLE
name. Failure carries `ok=false` and an error. The active connection is retained
for the acknowledgement; the next disconnect/re-advertisement applies the new
name, and startup reads it from NVS. These behaviors require target build and
device verification.

Identity matching prevents accidental selection errors; it is not cryptographic
ownership/authentication. This candidate does not implement a physical enrollment
button, BLE bonding or an owner secret. Controlled enrollment and resistance to
nearby unauthorized renaming remain open commercial release gates.

## Evidence and acceptance

On 2026-10-18, hardware-free tests compiled and executed the **actual C++ parser,
UTF-8 validator and transport-recovery policy helper** with the local native
compiler. Configuration tests check missing factory wiring, polarity, duplicate
pins and 12-bit PWM duty bounds. Run them with:

```bash
python3 -m unittest tests.test_esp32_protocol -v
```

These tests do not compile all Arduino BLE callbacks, Preferences integration,
FreeRTOS queue/BLE disconnect integration, or prove PWM behavior on every unit.
The standalone diagnostic is separate from the full sketch. On 27 October,
the full target build/upload passed on unit `5D1C`, with all four written region
hashes verified. USB identity/GPIO diagnostics, invalid rename rejection,
complete valid rename acknowledgements, saved-name persistence across two
software reboots and restoration of the factory name passed. The owner confirmed
all three production search lights blink together. A reproduced 64-byte USB
rename-reply truncation was corrected and the same sequence passed afterward.
The pre-flash 4 MiB SHA-verified backup remains private. The final report shows
`ble_connected=false` and stack advertising active; no radio scan or connection
was performed. Physical power-cycle and buyer BLE/provider checks remain open.
See the [factory handoff finding](findings/2026-10-27-esp32c3-factory-handoff.md).
Then verify visible R/Y/G/B/O,
searching/connection animation, real BLE GPIO acknowledgements, fragmented
rename, persisted name after power loss, reconnect by immutable identity,
duplicate nearby devices, metadata, queue overflow recovery, provider turns,
sleep/login/reboot, and removal.
Check LED changes remain responsive while notifications are fragmented under
load. Record every pass/fail/not-run. Successful USB factory build/upload and
first Q/GPIO checks do not establish customer Bluetooth pairing, BLE GPIO
commands, provider turns, or release qualification. The actual buyer's computer
must complete those checks; never pair this Mac during factory USB acceptance.

## Implementation references

- [Official Arduino-ESP32 BLE UART example](https://github.com/espressif/arduino-esp32/blob/master/libraries/BLE/examples/UART/UART.ino): NUS server/characteristic API structure.
- [Espressif Preferences API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/preferences.html): persistent NVS string storage.
- [Espressif LEDC API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html): Arduino 3.x PWM API and frequency/resolution constraints.
- [ESP32-C3 GAP API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/bluetooth/esp_gap_ble.html): advertised/GAP name updates.
- [ArduinoJson deserialization API](https://arduinojson.org/v7/api/json/deserializejson/): bounded identity-frame JSON parsing.
