# ESP32-C3 cable-only LED diagnostic

Physically confirmed by the owner on 26 October 2026 on the connected ESP32-C3
Super Mini unit. The chip reported revision 0.4, 40 MHz crystal and 4 MB embedded
flash. This is a standalone LED test, not Bluetooth/customer firmware.

| LED | ESP GPIO |
| --- | --- |
| Red | 3 |
| Amber | 2 |
| Green | 1 |

Outputs are active-high: each LED has its own series resistor and a common ground.
Do not substitute Nordic P0/P1 labels or Arduino Uno pin mappings.

On power, the test repeats red, amber and green individually for 1.4 seconds each,
then blinks all three together three times (650ms on/off). USB serial 115200 emits
phase labels and GPIO output readback. The test does not wait for a serial viewer,
start Wi-Fi/Bluetooth, install hooks, or connect to a computer-side bridge.

## Reproduce on the identified unit

Tested toolchain: Arduino CLI 1.5.2-rc.1, Espressif Arduino-ESP32 3.3.2. Build with native
USB CDC enabled:

```sh
arduino-cli compile \
  --fqbn esp32:esp32:esp32c3:CDCOnBoot=cdc,FlashSize=4M \
  --output-dir /PRIVATE/BUILD firmware/esp32c3_led_test
arduino-cli upload \
  --fqbn esp32:esp32:esp32c3:CDCOnBoot=cdc,FlashSize=4M \
  --port /dev/cu.REPLACE_WITH_IDENTIFIED_BOARD \
  --input-dir /PRIVATE/BUILD firmware/esp32c3_led_test
```

Rediscover and identify the USB unit before upload; serial paths can change.
Preserve existing flash/configuration first. Never flash the nRF nice_nano UF2
onto this ESP32. Standard Arduino upload writes its boot image, partition table
and application; it is not a read-only test. The original unit's complete 4 MiB
flash was backed up privately before this upload; no backup binaries belong in Git.

Actual acceptance and next setup boundary:
[26 October findings](../../docs/findings/2026-10-26-esp32c3-led-test.md).
