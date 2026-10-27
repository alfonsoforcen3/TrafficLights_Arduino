# Compatibility

| Component | Status |
| --- | --- |
| nice!nano-compatible nRF52840, described GPIO wiring | Verified prototype |
| CircuitPython 8.1.0 / UF2 bootloader 0.6.0 | Verified combination |
| macOS 26.6.2 / Apple Python 3.9.6 | Verified host |
| Local Codex hooks | Verified real prompt/stop dispatch |
| BLE colors / explicit error / automatic helper reconnect | Verified; serialized writes passed a two-minute Mac stress run |
| OLED Clawdy / working count / provider icons | Original nice_nano unit verified on Mac; native Windows acceptance pending |
| Other Python/macOS versions | Require acceptance tests |
| Native Windows automatic installation | Implemented; previous Windows BLE reported by owner, current revision native acceptance pending |
| Linux/WSL automatic installation | Unsupported |
| Arduino Uno/Nano wired sketch | Legacy separate firmware; Bluetooth unavailable |
| Ordinary ChatGPT chat / cloud-orchestrated Work command hooks | Unsupported |
| Claude Code / Gemini CLI / Cursor adapters | Installer/payload tests pass; real application acceptance pending |
| USB power input / cable and repeated power-off/on cycles | Pending production-source and assembled-unit acceptance |
| Signed/notarized consumer installer | Not provided; current helper is locally built |
| Wireless terminal discovery/enrollment | Candidate; hardware-free tests, clean-customer acceptance pending |
| Persistent laptop/nickname BLE rename | New nRF firmware candidate using NVM; existing flashed units require factory update or keep-name |
| ESP32-C3 UART protocol | Separate factory candidate; GPIO configuration and physical acceptance required; not interchangeable firmware |

A different nRF52840 board needs its own CircuitPython UF2, pin names, USB power-input documentation and hardware validation. Do not generalize a compatible bootloader label into an exact board specification. Preserve unsupported-platform limitations instead of letting an installer print a false success.

Use the [Windows setup guide](windows/INSTALL.md) and [current integration findings](windows/findings/2026-10-07-mac-integration.md). Do not equate hardware-free CI with native BLE or real-provider acceptance.
