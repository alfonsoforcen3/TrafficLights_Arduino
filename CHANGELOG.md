# Changelog

## 2026-10-27 — Factory ESP32-C3 and buyer-first enrollment

- Programmed unit `5D1C` with production ESP32-C3 firmware using its confirmed
  GPIO3/2/1 wiring, leaving it searching without a Bluetooth connection here.
- Corrected NimBLE target APIs, Arduino UUID naming collisions and a reproduced
  USB rename-reply truncation; added bounded transport recovery regressions.
- Made buyer setup the local-agent entry point, enforced BLE runtime, and added
  explicit provider consent, saved-profile replacement checks and optional
  exact-selected USB identity matching.
- Updated maintainer/handoff examples for explicit approved provider selection
  and added a real ESP32-C3 target compilation job.

Verification: 273 hardware-free regression tests passed. The full target built,
USB upload verified four region hashes, and USB identity/GPIO diagnostics,
invalid rename rejection, complete valid rename acknowledgements and persistent
names across two software reboots passed. Factory name was restored; owner
confirmed production search LEDs. No BLE scan/connection, host install or hook
changes were performed for this unit. Buyer-host BLE/provider acceptance,
physical power cycles and native Windows acceptance remain pending. See the
[factory record](docs/findings/2026-10-27-esp32c3-factory-handoff.md).

## 2026-10-27 — AI-assisted buyer setup and USB-powered product

- Made the implementation repository publicly readable and verified anonymous access.
- Added a buyer setup request and local-agent instructions for selecting, identifying,
  naming and configuring a pre-flashed Clawdy through guided onboarding.
- Standardized the product on USB power and a connection/light-status dashboard.
- Consumer packaging and physical customer acceptance remain separate release gates.

Verification: 258 hardware-free Python tests passed, including extracted-bundle
offline preflight/dry-run and intent-path cases. JavaScript syntax, dashboard
stale/unknown handling and the self-contained AI setup request passed local
checks. No board was contacted or flashed, and no installed runtime or hook was
changed. Clean-customer hardware and native Windows onboarding remain pending.

## 2026-10-19 — Wizard polish and accurate private website preview

- Polished terminal onboarding with five phases, optional colour, plain-output
  fallbacks and explicit verified/pending outcomes.
- Added a private responsive website preview using a faithful actual-model
  render, signal demo and setup walkthrough; the public QR page is unchanged.
- Tested and prepared the previously local onboarding, identity, observer-hook
  reliability and OLED phrase work for the owner's authorized commit/push.

See [iteration findings](docs/findings/2026-10-19-wizard-and-website.md).

## 2026-10-18 — Private customer onboarding candidate

- Follow-up hook audit: installed commands pointed into Desktop files observed
  as offloaded/dataless, with stalled source reads. New definitions use a local
  runtime observer; an explicit migration preserves existing settings and does
  not start the service. The observer now bounds input/network work, returns
  neutral provider output and does not fall back to opening USB devices or
  writing checkout logs. This fixes concrete blocking risks, not proof that
  hooks caused a model to finish its answer early.

- Added terminal BLE discovery/selection without USB data, provider preview and
  policy preflight, physical identification prompts and post-install verification.
- Added capability-checked persistent nRF52840 naming with immutable unit ID,
  preserving GPIO/OLED configuration; legacy firmware can keep its current name.
- Reject duplicate BLE names and validate enrolled identity before sending tracked
  states. Normal OS Bluetooth access and provider hook trust remain required.
- Added allowlisted private customer bundle with SHA-256 manifest, customer/agent
  setup guides and release acceptance steps. Nothing was published; the released
  host was not reconnected. The separately requested observer repair migrated
  existing hook commands without starting the bridge or granting hook trust.

This is a private candidate. Physical enrollment/power-cycle persistence, clean
customer setup and native Windows/provider acceptance remain pending. See
[candidate findings](docs/findings/2026-10-18-customer-onboarding.md).

## 2026-10-14 — OLED Clawdy and stable BLE writes

- Added optional SSD1306-compatible OLED animations with the 45 mm Clawdy proportions, red × eyes, rotating funny comments, larger top title, top working-only WIP count and smaller provider marks below.
- Added per-unit red/amber/green wiring overrides, preserving default profiles; original OLED unit uses P0.09 red / P0.10 amber / P1.11 green and owner-requested full green PWM duty.
- Sent bounded working counts/provider masks over BLE with incremental parsing and disconnect reset; multiple working provider icons rotate. Application identity comes from hooks, not browser/model detection.
- Serialized Mac BLE writes to avoid overlapping CoreBluetooth pending writes; exception types now appear in connection diagnostics.
- Added Mac/Windows installation, activation, update and removal instructions, plus explicit unsupported Linux/WSL status and hardware-free contributor checks.

Evidence: 49 local hardware-free tests pass; BLE R/Y/G/B/O and working/provider metadata acknowledged on Mac; 120-second concurrent-write observation had zero disconnect/startup/log errors. Owner confirmed LEDs, OLED animations and that repeated startup blinking stopped for now. Windows native acceptance, Linux activation, physical power cycles, Mac restart and extended uptime remain unverified. See [run findings](docs/findings/2026-10-13-ble-write-stability.md).

## 2026-10-01 — macOS Bluetooth tester iteration

- Added nice!nano-compatible nRF52840 CircuitPython firmware; corrected final wiring to P0.10 green, P1.11 amber, P1.13 red.
- Installed and verified local Codex prompt/stop hooks and explicit error/input signals. Preserved unrelated hooks and existing notify configuration.
- Added Nordic UART BLE, chunked GPIO acknowledgements, a Mac Bluetooth helper/login service, and automatic reconnect/heartbeat.
- Removed unsafe selection of Mac debug ports after USB disconnect.
- Added isolated installation, per-device name discovery/explicit name option, pinned/checksummed firmware provisioning, and persistent host session recovery.
- Documented pre-flashed customer onboarding, factory recovery, access approvals, hardware, USB power, troubleshooting, compatibility, and acceptance/release workflow.

Evidence: user confirmed physical green/amber/red; BLE acknowledgements for R/Y/G/B/O passed; helper restart restored a persisted red session and reconnected to BLE; seven hardware-free regression tests passed. Repeated MCU resets, USB power cycles, clean-user onboarding, and full Mac reboot are not yet established. This is a tester release, not a commercial safety certification.

Follow-up: the running helper connected automatically to TrafficLight-16DE with no Arduino USB device detected. Fresh BLE acknowledgements for R/Y/G/B/O passed and tracking was restored. Physical light confirmation, power-source verification, reconnect timing, and repeated switch cycles remain pending.


Reconnect follow-up: user reported green during work; host hooks selected amber but BLE was disconnected. Restarting the helper restored BLE and amber acknowledgement; user confirmed the light changed. Added bounded Bluetooth operation timeouts and a stalled-write regression test. Eight regression tests pass. Repeated power-cycle recovery remains to be measured.

Display follow-up: added a cancellable 1.5-second completion delay before green and 0.8-second input delay before blinking red; work/error changes remain immediate. Ten regression tests pass, including resumed-work cancellation and suppression of brief input signals. The prior end-of-turn colour sequence was an explicit hardware diagnostic.

Release documentation: consolidated multi-chat priority, completion/input settling, session recovery and integration limits in docs/MULTIPLE_CHATS.md. Eleven regression tests pass, including concurrent-chat priority and preservation of other chats when one ends.

## 2026-10-01 — local provider adapters

- Added automatic discovery and hook installation for supported local Codex, Claude Code, Gemini CLI and Cursor Agent; explicit --providers and --no-hooks remain available.
- Added provider/session namespaces and migration of older bare Codex IDs, preserving mixed-provider work.
- Added schema-specific settings merging/backups/removal, correct timeout units, silent Claude observers, Gemini ToolPermission filtering and Cursor lifecycle-only observers. Existing disabled hooks/policies are respected.
- Installed Claude Code hooks on this Mac without changing approved Codex hook definitions. The installer detects Codex and Claude here; Gemini and Cursor are absent and were not installed.
- Nineteen hardware-free regressions pass. Synthetic invocation of the installed Claude prompt/Stop/SessionEnd commands alongside this live Codex turn preserved amber and separate session records; BLE GPIO acknowledged Y. No paid model run was started to test Claude.
- Real Claude/Gemini/Cursor application dispatch and clean-customer installation remain acceptance tasks. Ordinary web AI chats, other apps without adapters and cloud VMs are not automatically tracked. Documented all adapters and extension workflow in docs/PROVIDERS.md.

## 2026-10-01 — presentation and commercial separation

- Added a vector product banner, customer-oriented README and documentation index.
- Added hardware-free CI, local documentation-link validation, issue/PR templates and security/contribution guidance.
- Documented production release gates and OpenCode/Windsurf integration candidates without claiming unsupported applications work.
- Owner selected private implementation plus public setup/docs and a signed Mac installer. Existing public copies cannot be recalled; the current alias helper is not a standalone signed consumer package. Commercial packaging and terms remain release work.

At that iteration, implementation and setup documentation were separated. Source visibility changed to public on 2026-10-27. Source history preserved and backed up locally. No standalone consumer installer is published.

## 2026-10-02 — Clawdy local website

- Added a Mac-local Clawdy website with CyberDuck alternate, explicit product/installer previews, Bluetooth setup and multi-session explanation.
- Preserved existing hook approvals and firmware backups. Verified BLE GPIO acknowledgements; 22 automated tests pass.

## 2026-10-06 — First Clawdy and Bluetooth connection lights

- Added per-unit green GPIO and Bluetooth-name profiles; first clawdy uses P0.09, P1.11 and P1.13. Original units retain their defaults.
- Added simultaneous searching blink and a nonblocking connection light show, followed by the latest tracked state.
- Verification reads the actual configured green GPIO and waits for the connection animation to finish.
- Provisioning preserves unit/calibration files in backups and handles macOS metadata/UF2 reset behaviour.
- Documented migration to another Mac without reflashing. Twenty-five automated tests pass; BLE GPIO delivery and the visual connection animation were confirmed on first clawdy. Second-laptop and physical power-cycle acceptance remain pending.

## 2026-10-06 — Release and agent laptop handoff

- Released first clawdy from the original Mac by disabling owned provider hooks and removing its login service; verified service and bridge listener absent.
- Added an agent handoff runbook, known unit identity/wiring, release checks and reinstallation instructions. New-laptop connection remains unverified.

## 2026-10-06 — Windows implementation and findings assignment

- Added a complete Windows-agent prompt covering native BLE, runtime/startup, provider hooks, permissions, release/recovery, regression tests, physical acceptance and commits.
- Added a redacted findings template and agent entrypoint. Windows implementation/installation remains pending on the Windows laptop; current installer remains macOS-only.

## 2026-10-06 — Native platform-aware installation

Installer selects macOS or Windows runtime paths, dependency sets and login launchers; provider commands use platform quoting. Windows login startup, cooperative shutdown, runtime connection configuration and portable test delays added. Windows report summarized without private email headers. Previous report branch was unavailable; native acceptance of this implementation is pending.

## 2026-10-07 — PWM dimming and Windows handoff integration

Green defaults to validated 50% PWM at 5 kHz; First Clawdy updated with backups, real BLE GPIO checks and human visual confirmation. Added safe cross-platform CircuitPython discovery, Gemini PowerShell literal command quoting/turn lifecycle, narrow legacy hook cleanup, bridge PID lifecycle and duplicate-instance rejection. Added portable regression tests and Windows CI. Native Windows acceptance of this revision remains pending; corporate policy is respected. Full findings and agent follow-up instructions recorded.
