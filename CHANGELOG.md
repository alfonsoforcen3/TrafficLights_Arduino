# Changelog

## 2026-10-01 — macOS Bluetooth tester iteration

- Added nice!nano-compatible nRF52840 CircuitPython firmware; corrected final wiring to P0.10 green, P1.11 amber, P1.13 red.
- Installed and verified local Codex prompt/stop hooks and explicit error/input signals. Preserved unrelated hooks and existing notify configuration.
- Added Nordic UART BLE, chunked GPIO acknowledgements, a Mac Bluetooth helper/login service, and automatic reconnect/heartbeat.
- Removed unsafe selection of Mac debug ports after USB disconnect.
- Added isolated installation, per-device name discovery/explicit name option, pinned/checksummed firmware provisioning, and persistent host session recovery.
- Documented pre-flashed customer onboarding, factory recovery, access approvals, hardware, batteries/switches, troubleshooting, compatibility, and acceptance/release workflow.
- Prototype battery label: JH 702030, 3.7 V, 300 mAh, 1.11 Wh, 25C. Clone charger specification and connector/terminal verification remain required before wiring/charging.

Evidence: user confirmed physical green/amber/red; BLE acknowledgements for R/Y/G/B/O passed; helper restart restored a persisted red session and reconnected to BLE; seven hardware-free regression tests passed. Repeated MCU resets, physical battery switch cycles, battery endurance/charging, clean-user onboarding, and full Mac reboot are not yet established. This is a tester release, not a commercial safety certification.

Follow-up: after the user reported connecting the battery, the running helper connected automatically to TrafficLight-16DE with no Arduino USB device detected. Fresh BLE acknowledgements for R/Y/G/B/O passed and tracking was restored. Physical light confirmation, power-source verification, reconnect timing, and repeated switch cycles remain pending.

Battery follow-up: user confirmed physical operation after automatic BLE reconnect. Supplier listing B0DP18ZVL7 claims lithium charging support; charging current and protection remain unverified. Recorded supplier evidence in docs/BATTERY.md.
