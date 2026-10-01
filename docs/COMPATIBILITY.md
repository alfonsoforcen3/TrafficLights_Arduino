# Compatibility

| Component | Status |
| --- | --- |
| nice!nano-compatible nRF52840, described GPIO wiring | Verified prototype |
| CircuitPython 8.1.0 / UF2 bootloader 0.6.0 | Verified combination |
| macOS 26.6.2 / Apple Python 3.9.6 | Verified host |
| Local Codex hooks | Verified real prompt/stop dispatch |
| BLE colors / explicit error / automatic helper reconnect | Verified |
| Other Python/macOS versions | Require acceptance tests |
| Windows/Linux automatic installation | Not supported by this installer |
| Arduino Uno/Nano wired sketch | Legacy separate firmware; Bluetooth unavailable |
| Ordinary ChatGPT chat / cloud-orchestrated Work command hooks | Unsupported |
| Gemini/Claude hook installation | Legacy examples, not currently verified |
| Battery charging/runtime / physical repeated off-on cycles | Pending actual battery and board checks |
| Signed/notarized consumer installer | Not provided; current helper is locally built |

A different nRF52840 board needs its own CircuitPython UF2, pin names, charger documentation and hardware validation. Do not generalize a compatible bootloader label into an exact board specification. Preserve unsupported-platform limitations instead of letting an installer print a false success.
