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

Reconnect follow-up: user reported green during work; host hooks selected amber but BLE was disconnected. Restarting the helper restored BLE and amber acknowledgement; user confirmed the light changed. Added bounded Bluetooth operation timeouts and a stalled-write regression test. Eight regression tests pass. Repeated battery-cycle recovery remains to be measured.

Display follow-up: added a cancellable 1.5-second completion delay before green and 0.8-second input delay before blinking red; work/error changes remain immediate. Ten regression tests pass, including resumed-work cancellation and suppression of brief input signals. The prior end-of-turn colour sequence was an explicit hardware diagnostic.

Release documentation: consolidated multi-chat priority, completion/input settling, session recovery and integration limits in docs/MULTIPLE_CHATS.md. Eleven regression tests pass, including concurrent-chat priority and preservation of other chats when one ends.

## 2026-10-01 — local provider adapters

- Added automatic discovery and hook installation for supported local Codex, Claude Code, Gemini CLI and Cursor Agent; explicit --providers and --no-hooks remain available.
- Added provider/session namespaces and migration of older bare Codex IDs, preserving mixed-provider work.
- Added schema-specific settings merging/backups/removal, correct timeout units, silent Claude observers, Gemini ToolPermission filtering and Cursor lifecycle-only observers. Existing disabled hooks/policies are respected.
- Installed Claude Code hooks on this Mac without changing approved Codex hook definitions. The installer detects Codex and Claude here; Gemini and Cursor are absent and were not installed.
- Nineteen hardware-free regressions pass. Synthetic invocation of the installed Claude prompt/Stop/SessionEnd commands alongside this live Codex turn preserved amber and separate session records; BLE GPIO acknowledged Y. No paid model run was started to test Claude.
- Real Claude/Gemini/Cursor application dispatch and clean-customer installation remain acceptance tasks. Ordinary web AI chats, other apps without adapters and cloud VMs are not automatically tracked. Documented all adapters and extension workflow in docs/PROVIDERS.md.
