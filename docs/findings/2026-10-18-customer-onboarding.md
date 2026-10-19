# Private customer onboarding candidate — 18 October 2026

## Scope and baseline

The owner requested a terminal onboarding flow for externally powered pre-flashed
toys, laptop+nickname naming, local provider hooks and an audit of customer access.
They explicitly asked to prepare privately and release later. The working tree
already contained unrelated OLED phrase changes, a findings draft and generated
output; these were preserved. The independent mascot checkout was not included.

The source repository is private. Public setup docs offered no installer and the
live QR landing page still has preview buttons. Existing install.py required a
supplied BLE name or USB discovery. Firmware had no BLE rename protocol.

## Implemented candidate

- `install.py --onboard`: dependency bootstrap, provider selection/policy preflight,
  bounded nearby UART scan, explicit selection, firmware verification, visual
  identification, naming, installation and BLE/visible-LED verification.
- Firmware Q reports hardware family, full device ID and rename capability.
  Framed rename requests require the selected ID, validate 29 UTF-8 bytes and
  persist to an owned nRF NVM record with readback. Foreign NVM is not overwritten;
  per-unit hardware_config.json is untouched. This is identity targeting, not an
  authenticated ownership or pairing protocol.
- Names combine shortened laptop/nickname and final eight ID hex digits. The
  full identity is saved in connection.json and checked before tracked commands.
  Duplicate names fail instead of selecting the first nearby board.
- Customer ZIP is built by explicit allowlist, with entry hashes and archive
  checksum. No Git history, factory firmware, CAD, supplier records, logs or
  customer settings are included. It contains Python source, stays private and
  does not replace the planned signed/notarized distribution.

## Verification and limits

Hardware-free tests use the existing isolated runtime interpreter. The system
Python initially lacked Bleak; that was an environment issue, not a BLE run.
No service installation, BLE connection, firmware flash, host release/reconnect,
purchase, public upload or commit was performed. One early onboarding test had
an incomplete mock and unintentionally ran an approximately eight-second BLE
scan; it found no matching toy and made no connection. Explicit module mocks
and fail-fast BLE guards were then added. Other tests use mocks/temp directories.
The owner separately requested hook reliability repair: the coordinator migrated
8 existing Codex and 9 Claude observer commands into the local runtime, with
backups and command-only diff verification. No service was started or hook trust
granted. See the hook reliability findings for that authorized local change.

The customer archive was extracted into a temporary directory: its standalone
offline `install.py --onboard --dry-run` command and compilation of every included
Python module passed without dependencies, downloads or access to hardware.
Documentation link checking and Git whitespace checks passed. The ESP32 protocol
header was compiled and executed with native C++ for ten parser/configuration
tests; the full Arduino sketch was not compiled because the ESP32 toolchain is
absent. This does not establish Arduino API compatibility or board acceptance.

Initial integrated run: **100 hardware-free tests passed**, no skipped tests on
this Mac. Read-only peer review caught a possible ESP32 first-query queue race;
queue clearing now occurs before re-advertising on disconnect, preserving input
already queued after connection. Full Arduino build/physical validation is still
pending. nRF rename storage is a single checked record, not a power-loss atomic
transaction: an interrupted write can require recovery to the factory label.

Final preparation after specialist reviews: **134 tests passed in 6.642 seconds**
with no skips. ESP32 PWM/overflow and invalid nRF input fixes are covered by
scoped tests. Bluetooth cleanup timing tests no longer rely on 30 ms scheduling.
The subprocess EOF test now separates bounded interpreter startup from its
unchanged two-second handler deadline; the prior failure is recorded in the
hook reliability report. Archive manifest/checksum, installed-observer equality,
and extracted offline onboarding passed. Documentation links and whitespace
checks passed. The private artifact is dist/clawdy-private-candidate.zip; no
Git commit or publication was made.

Run the customer enrollment acceptance section in docs/TESTING.md on an assembled
toy and clean laptop. Specifically verify NVM persistence on the actual pinned
CircuitPython build, physical selection with two toys, external-power cycling,
permissions, hook review/real dispatch, restart and removal/reinstall.

ESP32-C3 requires its own factory firmware and confirmed GPIO/polarity. Protocol
recognition in the host is not proof an arbitrary ESP32 board works. Never use
the nRF52840 UF2 on ESP32 hardware. Physical ESP32 and Windows acceptance remain
pending. Existing battery/charger limits remain unchanged.

## Publication handoff

After acceptance and owner approval: choose signed binary distribution or approve
source-containing customer bundle terms; publish a versioned artifact and checksum
to TrafficLights_Setup; update the existing public user-site `clawd-mascot-3d/`
installer link; verify anonymous download, clean extraction/install and exact QR
destination. Keep private source history, keys, logs and factory records private.
