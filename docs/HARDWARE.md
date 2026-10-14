# Hardware and factory provisioning

The verified prototype has an nRF52840 and identifies its bootloader as nice!nano, Board-ID nRF52840-nicenano, UF2 0.6.0 / SoftDevice S140 6.1.1. A bootloader identity does not prove a clone has the genuine board's charger or protection circuit. Verify the supplier schematic and labels for each production board revision.

| LED | Nordic GPIO | Connection |
| --- | --- | --- |
| Green | P0.10 | GPIO → 220–330 Ω resistor → LED anode |
| Amber | P1.11 | GPIO → 220–330 Ω resistor → LED anode |
| Red | P1.13 | GPIO → 220–330 Ω resistor → LED anode |
| All cathodes | GND | Common ground |

P0.10 means port 0, pin 10. Do not substitute Arduino pin 10. Fit one resistor per LED. Check polarity, common ground, soldered headers, and breadboard row continuity. A board resting over unsoldered headers is not a connection; software output reports cannot detect that defect.

For soldering this board follow its supplier's temperature and dwell guidance. The genuine nice!nano manufacturer specifies approximately 270–300°C; our earlier generic soldering-iron advice was not board-specific. See [manufacturer preparation](https://nicekeyboards.com/docs/nice-nano/getting-started/). Do not use header locations from another revision as battery terminal evidence.

## Factory load

Use scripts/flash_nicenano.py as described in INSTALL.md. It checks the board ID and backs up CURRENT.UF2 / existing files. The pinned official UF2 is:

- URL: https://downloads.circuitpython.org/bin/nice_nano/en_US/adafruit-circuitpython-nice_nano-en_US-8.1.0.uf2
- SHA-256: `454ad2c9d24a82199fe3f59a977b9c04519c1901021ed639dd4a7ed90de7d3f5`
- Sources: [CircuitPython board page](https://circuitpython.org/board/nice_nano/) and [manufacturer flashing instructions](https://nicekeyboards.com/docs/nice-nano/getting-started/).

Copy boot.py, ble_link.py, battery.py, connection_display.py, pwm_led.py, and code.py; reset once after boot.py changes. CircuitPython enables USB data only, with its console disabled. Firmware needs only built-in libraries. It also advertises Nordic UART BLE.

USB/BLE commands are G, Y, R, B, O, T; Q returns a newline JSON GPIO report. USB-only X resets the board for maintenance. T is a firmware light cycle; the host acceptance helper uses explicit states instead.

The default BLE name comes from the CPU UID suffix; a per-unit profile may override it. Read the actual Q response or BLE advertisement and label each unit with its exact TrafficLight-XXXX name. Check names are unique within each batch; the current four-hex suffix is not a production serial-number system. Record batch ID, supplier/revision, firmware commit, name, wiring, visual LED results, and battery/charging acceptance before shipment. Do not ship devices that only pass software checks.

Customers should receive a pre-flashed, assembled, tested unit. USB provisioning is for the factory, firmware updates, and recovery—not ordinary customer onboarding.

## Per-unit wiring and Bluetooth name

The original profile remains P0.10 green, P1.11 amber, P1.13 red. The replacement unit requested on 2026-10-05 uses P0.09 green (the `009` silkscreen below `010`, which reads `600` upside down), with amber and red unchanged, and the requested BLE name `first clawdy`. Provision it only after confirming its actual board/bootloader identity.

On a verified compatible board, `/hardware_config.json` selects the unit profile:

```json
{"green_pin": "P0.09", "ble_name": "first clawdy"}
```

Without this file, firmware retains the original P0.10 and UID-based BLE name. Green accepts P0.10, P0.06, or P0.09; the BLE name must fit 1–29 UTF-8 bytes. GPIO reports include `green_pin` and report its actual pin rather than mislabelling it P0.10. Hardware verification supports both profiles. Reload after profile changes, discover the actual advertisement, then update the Mac service using `--no-hooks --ble-name "first clawdy"`. A name change alone is not proof of Bluetooth delivery.

Replacement unit provisioning on 2026-10-05: bootloader Board-ID `nRF52840-nicenano`, version 0.6.0 / S140 6.1.1; pinned CircuitPython 8.1.0 installed after preserving CURRENT.UF2 and initial files. CPU UID `8063344647CEF029`; actual BLE name `first clawdy`. BLE GPIO acknowledgements passed R/Y/G/B/O with P0.09 green and normal tracking restored. Existing provider hooks were preserved with `install.py --no-hooks`. Twenty-two automated tests passed. The user confirmed all three LEDs visibly lit; battery-only cycling and Mac restart have not been tested for this unit. Clone battery percentage/charging remain unverified.

## Bluetooth connection lights

Firmware uses a nonblocking connection display. While disconnected/advertising, all three LEDs blink together, 0.4 seconds on and 0.4 seconds off. On each Bluetooth connection, red → amber → green repeats twice (0.16 seconds per step, about one second total), then the latest tracked state resumes. Commands remain processed during the animation; heartbeats do not restart it. Starting tracked state is off until a host state arrives, avoiding a false completed indication. GPIO reports distinguish `searching`, `connected_show`, and `tracking`; verification waits for tracking before comparing normal colours. Searching consumes additional LED power and does not indicate an AI error or completion.

Validation on first clawdy: searching reports included simultaneous all-on and all-off; reconnection reported searching → connected_show → tracking and restored working/amber. BLE R/Y/G/B/O acknowledgements passed; 25 automated tests pass. Firmware files were backed up locally. The user confirmed the simultaneous blink and connection light show looked good. Physical power-cycle acceptance remains separate.

## Green PWM brightness

As of 2026-10-07 green uses 5 kHz PWM at 50% duty by default; red and amber retain full digital intensity. `hardware_config.json` may include `"green_brightness": 0.5` (finite range 0–1). A value of 1 restores full green duty; 0 suppresses green illumination. Default applies to supported green profiles, not just First Clawdy. Reports expose green_pwm_duty and green_pwm_frequency alongside boolean GPIO intent; they do not measure emitted brightness. Preserve the per-unit profile when updating. First Clawdy passed BLE R/Y/G/B/O; the owner confirmed all lit and green looked good. See [integration findings](windows/findings/2026-10-07-mac-integration.md).

## OLED-equipped original unit — 2026-10-11

This unit was identified directly over USB as nice_nano, CircuitPython 8.1.0,
UID ending 16DE. Its actual BLE name is `TrafficLight-16DE`; this is separate
from first clawdy. Owner-confirmed wiring is red P0.09 (`009`), amber P0.10
(`010`), green P1.11 (`111`). Its explicit per-unit profile is:

```json
{"red_pin":"P0.09","amber_pin":"P0.10","green_pin":"P1.11","green_brightness":1.0,"oled_enabled":true}
```

The owner requested full green PWM duty: 65535 at 5 kHz. Existing default
profiles retain 50% duty and their original wiring. Red/amber overrides accept
only the documented original or this unit's pins; LED pins must be distinct.

The four-pin OLED connects GND → GND, VCC → 3.3 V, SCL → P0.20 (`020`),
SDA → P0.22 (`022`). It responds at 0x3C and successfully displayed an
SSD1306-compatible 128×64 framebuffer; the actual controller/vendor remains
unconfirmed. Do not infer a module's pin order from another supplier's photo.
`oled_display.py` is optional, enabled only by the profile, and must precede
`code.py` when copying firmware. A display failure is reported as `oled_error`
and does not disable LED/BLE handling. The drawing scales the 45 mm model's
front silhouette uniformly, including four quarter-height legs. Yellow thinks,
green bounces, red shakes with × eyes, blinking red requests input, and an
unconnected board displays LOOKING / FOR HOST. Comments describe aggregate
colour status, not task content or provider identity. No transcripts go to BLE.

See [Mac/OLED verification](findings/2026-10-11-oled-mac.md) for current limits.

### OLED session count — 2026-10-13

The BLE bridge sends `N<count>\n` before its three-second state heartbeat.
`session_count.py` parses fragmented metadata without treating it as a colour
command, and is installed before code.py. Existing colour commands are retained.
The right-column title reads `Clawdy`. At the top left in the OLED yellow band, one centered line
shows `N WIP` (up to `9999 WIP`), with a smaller provider graphic below. Unknown/disconnected counts show `-- WIP`; the right status
text shows LOOKING / FOR HOST when disconnected. The last count is cleared
on disconnect. Only numeric totals and provider flags are transmitted; no session identifiers
or chat content are sent to the board. Wire totals are capped at 9999.

The total counts only hook-reported working (`Y`) sessions across providers.
Ready (`G`), input-waiting (`B`) and errored (`R`) sessions are excluded. It is
not a count of open UI windows. Abandoned working records still follow the
existing 24-hour expiry policy. Colour continues to reflect the most urgent
tracked state, so a blinking red light can coexist with other working sessions.
The report exposes `session_count` and `session_count_kind=working` for
verification. USB-only host transport does not send this BLE metadata.

### Working-provider icons — 2026-10-13

BLE metadata also includes `P<mask>\n`, with bits Claude=1, Codex/OpenAI=2,
Gemini=4, other/unknown=8. Only Y sessions contribute; their provider comes from
the existing hook namespace. The board reports `working_provider_mask`.
Multiple working providers rotate every five seconds alongside phrase changes;
one provider's ready/input/error state removes it from this working mask. When
none is working or BLE is disconnected, Clawdy returns as the neutral companion.
The right title remains Clawdy and the top-left line remains the total `N WIP`.

Claude displays the owner-approved Clawdy animation. Codex displays a monochrome
OpenAI Blossom with CODEX label; Gemini displays a code-drawn monochrome star
with GEMINI label. Other/unknown providers show a neutral question mark, never a
model inferred from Cursor's application name. Logo shapes remain static with
a small moving progress dot; Claude retains its expression/movement reactions.
`provider_icons.py` must be copied before oled_display.py and code.py.

This identifies local applications, not models or browser tabs. Ordinary ChatGPT,
Claude and Gemini web conversations still have no hook integration here. A
Gemini CLI install needs its normal configured/reviewed hooks; displaying a
synthetic Gemini signal is not real-provider acceptance. No new provider was
installed by this update. Only masks/counts/status go to BLE, not identifiers or
transcripts. The OpenAI mark is rasterized from the [official cookbook asset](https://github.com/openai/openai-cookbook/blob/main/examples/voice_solutions/realtime_translation_guide/livekit-translation-demo/public/brand/chatgpt-blossom-white.svg);
logos remain their owners' marks and are used here as provider identification.
