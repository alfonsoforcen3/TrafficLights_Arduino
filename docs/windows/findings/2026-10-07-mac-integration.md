# First Clawdy — Mac integration and Windows handoff, 2026-10-07

## Scope and baseline

Baseline source: `3401a2d`. The owner supplied a Windows companion prompt because corporate policy prevented USB storage writes and Git push. Its description of domain/DLP restrictions is owner-reported, not independently diagnosed on this Mac. Private account and device addresses are omitted. No policy bypass was attempted.

This Mac had no bridge listener or enabled login service at baseline. First Clawdy mounted as CircuitPython 8.1.0 / Board ID nice_nano. Its existing profile selected P0.09 green and BLE name `first clawdy`; amber P1.11 and red P1.13 were preserved. No UF2 or bootloader update was needed.

## Implemented changes

- Green uses 5 kHz PWM with default on-duty 32768/65535. Amber/red remain digital at full on-level. The boolean LED interface keeps blink/search/connection animations compatible. `green_brightness` optionally selects a finite value from 0 to 1; reports include PWM duty/frequency. This is electrical duty, not a calibrated light-output or battery-saving claim.
- A separate `pwm_led.py` is copied before `code.py`. The flasher backs up existing firmware and per-unit configuration. Windows drive-letter discovery and Mac mounted-volume discovery refuse multiple CircuitPython candidates; wrong-board validation still precedes application writes. Bootloader provisioning remains possible before CIRCUITPY exists, unlike the supplied draft's premature missing-drive rejection.
- Gemini Windows commands use PowerShell's call operator and literal single-quoted paths, escaping embedded apostrophes. Source: [Gemini hook runner](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/hooks/hookRunner.ts) and [shell selection](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/utils/shell-utils.ts), inspected 2026-10-07. Other providers retain their current shell commands. Gemini stays working through tool events and completes at AfterAgent; the redundant BeforeModel adapter was removed.
- Legacy Gemini handlers are removed only with this project's script/provider evidence; unrelated similarly named hooks remain. Existing hook namespace removal, backups and repeated-install behavior remain covered by tests.
- Bridge binds its port before starting BLE; duplicate startup fails instead of competing for hardware. PID file is informational and cleaned on cooperative shutdown; it is never used to kill an arbitrary process. Connection-file fallback and socket shutdown already existed in the baseline. Accepted sockets now have a bounded read timeout.
- Hardware-free tests use the native virtual-environment path. Windows Python 3.12 CI coverage was added; hosted run result is separate from local results.

## Verification performed on Mac

| Check | Result and evidence |
| --- | --- |
| Firmware backup and update | Passed; local ignored `.backups/board-*` preserves prior files/profile; installed source files matched checkout |
| Correct profile retained | Passed; P0.09 / first clawdy unchanged |
| Firmware USB maintenance reset | Passed using USB-only X; not a physical power cycle |
| USB report | Passed; duty 32768, frequency 5000, no BLE error |
| BLE R/Y/G/B/O | Passed; connected ble:// peer and transport=ble GPIO reports in tracking phase |
| Visible LEDs / dimmed green | Owner confirmed all lit and green looks good |
| Two concurrent sessions | Passed synthetic live bridge test: one finishes → aggregate remains Y; both finish → settled G |
| Duplicate bridge process | Passed; occupied-port failure before BLE startup |
| Cooperative shutdown / release | Passed; temporary helper exited, bridge.pid removed, TCP listener absent; no Mac login service enabled |
| Tests / documentation | 32 hardware-free tests passed; documentation links and whitespace checked |

A temporary existing Mac Bluetooth application was used without reinstalling provider hooks or enabling login startup. Runtime script copies were backed up locally. Test sessions were removed. The Mac helper was stopped after verification so Windows can reclaim the unit.

## Not run / remaining production gates

Native Windows execution of this revision, real Gemini/Claude dispatch, Windows startup after logout/reboot, clean-machine setup, sleep/wake, physical power cycles and extended runtime were not run here. The owner reports previous Windows success; this does not certify the new hook command or lifecycle behavior. Battery sensing/percentage/charging remain unverified and report null rather than invented values. Signing, consumer packaging and firmware rollback acceptance remain separate work.

## Windows next steps

Use [Windows INSTALL](../INSTALL.md). Release any other controlling host, pull this iteration, preview providers, run the full installer because hooks changed, review normal provider trust and start fresh provider sessions. Do not attempt firmware writes to a company-blocked USB drive: this unit is already updated. Verify live BLE GPIOs, actual prompt/tool/completion turns, mixed providers and login restart, then append a new sanitized run report using the findings template. Request normal IT approval for policy-blocked dependencies or startup instead of bypassing controls.

Rollback uses the previous Git revision plus the locally preserved board files including per-unit configuration. Do not flash a different board UF2 to resolve a host policy problem. Record the integration commit with `git log -1 --oneline` after pulling; this report is committed together with the tested changes.

## Hosted CI correction

The first hosted run for `25d3105` passed macOS and both Linux jobs; Windows passed 31 of 32 tests. Its sole failure was the firmware copy-order test matching a POSIX slash in a native Windows path (StopIteration), not a firmware/installer failure. The test now compares Path.name and retains the same dependency-order assertion. Source: [initial workflow](https://github.com/alfonsoforcen3/TrafficLights_Arduino/actions/runs/37583527578). New hosted status must be checked separately; physical Windows/provider acceptance remains pending.
