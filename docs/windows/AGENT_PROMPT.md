# Current Windows acceptance assignment (2026-10-07)

The implementation now exists. Pull the current main branch and read INSTALL.md, docs/windows/INSTALL.md and docs/windows/findings/2026-10-07-mac-integration.md before using the detailed checklist below. Its earlier implementation/pending language is historical: verify and repair the current code instead of overwriting it with another whole-file version.

Start with `git pull --ff-only`, `py -3 scripts/provider_setup.py --detect`, and `py -3 install.py --ble-name "first clawdy" --providers claude gemini`. First Clawdy already has the PWM firmware installed on Mac; no CIRCUITPY write is required. Review provider trust normally and restart existing sessions if needed. Verify real Gemini and Claude turns, concurrent chats, BLE reconnect and user-login startup. Gemini Windows commands use PowerShell `&` and single-quoted literal paths; do not replace them with cmd.exe or POSIX quoting.

Corporate policy is a boundary, not a defect to bypass. Do not disable DLP or alter trust/security records. If Git push is blocked, supply a sanitized patch/report through a user-approved channel; do not claim a local commit was pushed. Record each passed, failed, blocked and not-run check. Do not commit private account names, addresses or raw logs.

---

# Windows implementation, installation and findings handoff

Copy this complete prompt into the coding agent on the Windows laptop, after cloning the public repository. This is an implementation assignment, not evidence that Windows support already exists. Read the current code and repository instructions before executing it.

---

You are working on TrafficLights_Arduino for the owner of First Clawdy. Build, install and verify a native Windows companion for the already flashed BLE toy, and record reproducible findings in this repository. Persist through implementation and testing where authorized; do not stop at a proposal. Never fabricate physical observations, compatibility claims or test results. Ask for genuinely missing physical information or required OS/user actions, while continuing independent work.

## 1. Intended outcome

First Clawdy must receive local AI lifecycle states from this Windows laptop over Bluetooth. It must reconnect after board power interruption and helper restart, and start at user login using a documented user-level mechanism. The owner needs an agent-friendly setup and troubleshooting workflow, plus a findings log that preserves successes, failures and unresolved limitations for product engineering.

Deliver working Windows code and installation on this laptop where possible, relevant tests, a clean release/handoff path, documentation, and a findings report. If hardware or OS access blocks part of the work, finish the independent parts and clearly distinguish implemented from physically verified behaviour. A running process, paired device or simulated test is not proof that the board receives commands.

## 2. Known hardware and current state

- Device name is exactly `first clawdy`, including the lower-case spelling and space. This is the intended target, not the original developer device TrafficLight-16DE.
- It is a nice!nano-compatible nRF52840 clone. Bootloader identified itself as Board-ID nRF52840-nicenano, version 0.6.0, S140 6.1.1. Bootloader identity does not establish the exact USB power-input or component revision.
- CircuitPython 8.1.0 is already installed. CPU UID was recorded as 8063344647CEF029.
- Per-unit hardware_config.json on the board selects green P0.09 and BLE name first clawdy. Green's silkscreen is 009; upside down it reads 600. It is NOT P0.06 or Arduino D9. Amber is P1.11 and red P1.13. Each LED has its own series resistor and shares ground.
- Firmware is already installed and was verified over BLE on macOS. The user confirmed all three LEDs lit, and confirmed the connection animation looked good.
- While looking for BLE, all LEDs blink together, 0.4 seconds on/off. On connection, red → amber → green repeats twice, 0.16 seconds per step. Firmware then resumes the latest host state. Connection display is nonblocking; it must not turn completed/green merely because it connected.
- The previous Mac's integration was disabled on 2026-10-06. Owned hooks and login service were removed; the bridge listener and login service were verified absent. Do not assume they remain absent forever: ask the owner to release any competing host if needed. Do not send messages to another chat or alter another computer without user authorization.
- Power can be external USB. This setup does not require a USB data connection to Windows. Do not reflash, rename, change wiring or reset per-unit configuration merely to perform a laptop handoff.

## 3. Read the repository and establish a baseline

Read AGENTS.md, INSTALL.md, docs/COMPATIBILITY.md, docs/HARDWARE.md, docs/LAPTOP_HANDOFF.md, docs/PROVIDERS.md, docs/TESTING.md. Inspect the current git status, branch, HEAD and remote. Preserve unrelated work and the separate ignored claude-mascot-3d checkout. Use a codex/ branch for implementation unless the user specifically requests another branch. Avoid unrelated package/model changes.

The current install.py selects native macOS or Windows and includes a Windows
startup implementation. Native Windows BLE and real-provider acceptance for
this revision remain pending. The Mac helper is an alias app requiring its
runtime and is not a signed Windows executable. Do not treat hardware-free
Windows tests as physical qualification. Use docs/windows/INSTALL.md for the
current implementation and record acceptance results on the actual laptop.

Run applicable hardware-free baseline tests using an isolated environment. Record the command, versions, result and failures before editing. Identify whether any test assumes POSIX paths, launchctl, PyObjC or macOS app bundles. Keep Mac coverage when adding Windows support. No untested platform should be reported as supported.

## 4. Interview and inspect the Windows machine

Collect only the details needed for this product. Record a redacted summary:

- Windows edition/build, CPU architecture, native PowerShell/Python version and Git availability.
- Whether the agent executes natively on Windows, in WSL, or in a remote/container environment. Start with native Windows; WSL BLE/localhost forwarding is a separate compatibility target.
- Bluetooth adapter presence, enabled state and Windows device/driver health. Ask the user to use normal Windows settings for any permission or driver action. Do not disable protections, edit privacy databases, or require administrator rights unnecessarily.
- Confirm First Clawdy is powered, nearby and searching. Obtain the user's visible confirmation. A Mac BLE peer identifier is not a Windows address; rediscover it.
- Detect installed supported AI tools and their versions without issuing paid AI requests. Distinguish installed executable/settings evidence from ordinary browser chats. Do not install providers the user did not request.
- Ask for the first provider to test if several are available; continue generic companion work while awaiting that preference.

Use read-only OS commands or documented APIs for inventory. Avoid collecting full environment dumps, chat logs, tokens, passwords, unrelated device inventories or exact user-home paths in committed findings. If Python/Git is absent, use official vendor sources and normal installation approvals. Never request OS passwords in chat.

## 5. Research platform details from primary documentation

Before relying on platform-specific behaviour, consult current official documentation and record exact supporting links and the date accessed. Required areas include:

- Bleak's Windows/WinRT backend, scanning and characteristic discovery, notification handling, connection timeouts, adapter limitations, COM apartment/event-loop requirements and the behaviour of the chosen packaged/background launch context.
- Official Python Windows launcher, venv and interpreter paths; compatible Python/Bleak dependencies and availability on this machine's architecture.
- Official Microsoft guidance for the selected user-login startup mechanism and Bluetooth permission/OS troubleshooting. Choose one startup mechanism and document it fully, rather than installing several competing helpers.
- Current official hook schemas, support and command execution rules for each installed provider. Verify native Windows vs WSL support separately for Codex, Claude Code, Gemini CLI and Cursor.
- If packaging an executable, verify Windows packaging and Bluetooth behaviour rather than blindly porting py2app. Installer signing and SmartScreen reputation are release gates; never call a local unsigned build signed or commercially ready.

Keep provider recommendations grounded in installed versions. Mark unsupported/untested combinations explicitly. Do not bypass hook trust, permission prompts, workspace trust or execution policies.

## 6. Design the smallest maintainable Windows implementation

Inspect at least install.py, manage_hooks.py, scripts/codex_setup.py, scripts/provider_setup.py, scripts/claude_setup.py, scripts/traffic.py, scripts/bridge.py, scripts/ble_transport.py, scripts/dashboard.py and tests. Reuse platform-neutral protocol/aggregation logic; isolate platform-specific installation, paths, startup and packaging. Preserve the working Mac backend.

Prefer one centralized runtime-path/interpreter abstraction over scattered hard-coded replacements. Use a documented per-user Windows runtime location (for example under LOCALAPPDATA), an isolated venv with its Windows Scripts/python.exe, a durable connection configuration and logs with bounded retention. Decide where hook entrypoints live and keep paths stable. Handle non-ASCII user names and spaces. Derive the user's actual paths rather than copying a developer's machine.

Avoid macOS-only dependencies on Windows. Pin/test a compatible dependency set and document its rationale. Do not silently install py2app/PyObjC on Windows. Do not invoke Unix tools, launchctl, shell quoting or kill commands from Windows paths. Implement the actual service lifecycle used by install, status, disable/release and re-enable, not just a platform guard bypass.

Keep TCP command ingestion on loopback, with status and hardware delivery evidence. Keep the dashboard on loopback and read-only. Preserve strict Host checks, route restrictions, no arbitrary CORS, stale-data handling and omission of private prompts/session contents from the public-facing API. Do not open firewall ports or bind to 0.0.0.0 for convenience. If WSL interop becomes necessary, design and test it explicitly; do not expose local control to the network.

Separate physical test overrides from normal provider state aggregation. Commands must not be forwarded to unrelated serial devices if BLE is selected or the integration was disabled. Inspect the existing serial fallback when implementing a robust Windows release path. Use an explicit transport selection and fail safely if the intended board is unavailable.

## 7. Implement and prove the BLE transport

Firmware uses Nordic UART Service:

- Service: 6e400001-b5a3-f393-e0a9-e50e24dcca9e
- Host writes RX: 6e400002-b5a3-f393-e0a9-e50e24dcca9e
- Host receives notifications TX: 6e400003-b5a3-f393-e0a9-e50e24dcca9e

Verify these from current firmware, not just this prompt. Scan by the exact configured name plus available service evidence. Use the device returned by Windows discovery and rediscover after disconnects; do not hard-code the Mac's peer UUID or assume a stale address is reliable. Do not choose the first BLE device found. Explain whether Windows settings pairing is required by the actual tested backend; this toy's current service has not been established as requiring manual settings pairing.

Start notifications, reconstruct fragmented newline JSON reports, validate the expected firmware identifier, and retain current connection/transport/error evidence. Preserve bounded scan/connect/write/disconnect operations, recovery/backoff and shutdown. A malformed notification must not kill the companion; an ACK from the wrong device must not qualify success.

Light commands are G, Y, R, B and O; Q reports GPIO state. USB-only X resets the board and must not become a BLE reset endpoint. T is an explicit firmware light test; it must not be used as a fake error or silent acceptance proof.

Report fields include firmware, mode, green_pin, actual GPIO keys, transport, ble_name and display_phase. First Clawdy should report P0.09, P1.11 and P1.13. During searching/connected_show the output lights intentionally differ from tracked mode; wait for tracking before asserting ordinary colours. Reconnect must send the latest host aggregate and restore notification delivery. Merely establishing a BLE connection without current GPIO acknowledgements fails acceptance.

## 8. Installation and login lifecycle

Implement a supported Windows entrypoint (existing install.py if refactored cleanly, or a documented platform entrypoint). It must support a supplied exact board name, initial installation, safe repeat installation, update without hooks, status, full disable/release, re-enable and recovery. It must preserve unrelated settings, original hook order where relevant and user-disabled provider policies.

Choose and justify a per-user login mechanism: a user-level scheduled task or a documented Startup entry may be appropriate. Verify permissions, working directory, exact interpreter, quoting, hidden/background operation, clean shutdown and duplicate-process prevention. Do not promise startup before login unless explicitly implemented and tested. Handle a port already in use without killing an unrelated application. Dashboard failure must not stop core light tracking.

A repeated installer run must not duplicate startup entries or hooks. Disable must remove only owned hooks/startup items and stop the specific companion process, release BLE, and prevent automatic reconnection from this laptop. Preserve firmware, calibrated profiles and intentional backups. Runtime/package deletion is a separate operation and should not be performed merely to release Clawdy.

Document Python launcher fallbacks instead of assuming `python3` exists on Windows. Use PowerShell examples actually tested on the Windows laptop. Commands for the current unsupported Mac-only installer must never be labelled working Windows commands until implementation passes.

## 9. Provider integration

Preview detection first; then install adapters for detected supported tools within the user's authorized installation request. Keep unrelated hooks/settings. Back up each changed configuration, including sufficient rollback metadata, before writes. Validate JSON and avoid truncation or replacing whole configs to insert one owned hook.

Build command strings according to the provider's documented Windows shell/argv semantics. POSIX shlex.quote is not Windows quoting. Test a checkout path and Python executable path containing spaces, and non-ASCII paths where supported. Keep lifecycle stdout within each provider's contract so hooks do not break agent operation. Failures in the light integration must not falsely approve/deny tools or silently alter agent permissions.

Preserve session isolation and state priority: input/approval B > error R > working Y > completed G. A completed session must not turn green while another is working. Preserve the settling behaviour that avoids end-of-turn flicker; record actual transitions and any latency. Provider output text, prompts, private arguments and credentials must not be forwarded into logs or BLE payloads.

Verify one real prompt/completion with the user's installed provider, then supported real approval/input and error cases. Synthetic commands are separate tests. Do not deliberately damage files or trigger a paid/destructive action to manufacture an error. Additional provider acceptance remains pending until actually run on this platform. Do not claim generic browser ChatGPT/Gemini/Claude tracking.

## 10. Execute a layered acceptance plan

For each test record expected result, actual result, transport evidence, human observation, elapsed reconnect time where relevant and pass/fail/blocked/not-run. Never count not-run as passed.

1. Baseline hardware-free tests, formatting/diff and docs checks.
2. Dependency/environment creation, repeat install and update without hooks; unrelated config preservation and rollback.
3. Native Windows BLE scan, exact board discovery, subscribe, current Q/heartbeat report and tracking display phase.
4. Red, amber, green, blinking red and off acknowledgements over BLE, followed by normal tracking restoration and visible confirmation.
5. Searching blink and connection sequence, verified by both reports and user observation; latest working state resumes after connection, not a false green.
6. Real installed-provider prompt, finish, supported input/approval and error; two simultaneous chats, then mixed providers if available.
7. Board unplug/replug using external USB power. Record ten cycles if practical, including each timing/failure. A software reset is not a physical power-cycle test.
8. Helper restart, Windows user logout/login, Windows reboot, Bluetooth off/on and laptop sleep/wake as separate tests. State persistence and automatic reconnect are required outcomes to verify, not claims to assume.
9. Board absent during startup; stale BLE address; lost notify subscription; interrupted write; malformed/fragmented report; rapid reconnects; duplicate helper; occupied ports. Verify recovery, bounded logs and actionable diagnostics.
10. Read-only dashboard data, disconnect/stale behaviour, hostile Host/route requests and no private data disclosure.
11. Full release: helper stopped, startup absent/disabled, owned hooks removed, listener absent, BLE released; unrelated settings remain. Re-enable and rerun relevant acceptance.
12. Confirm Mac regressions remain covered. Add a Windows CI job for meaningful hardware-free tests once they are portable. Passing CI does not replace physical Windows BLE/provider tests.

Do not repeat successful hardware tests without a change/failure that justifies it. Keep user informed of material progress and blockers. Never request a Windows reboot while the user has unsaved work without coordinating that physical action.

## 11. Troubleshooting and escalation

Record the symptom, what layer it concerns, the specific evidence, hypothesis, intervention and result. Include OS/Python/Bleak/provider versions and a redacted error code/message. Distinguish no advertisement, adapter issue, competing host, GATT/notification failure, COM/event-loop issue, startup path/permission issue, hook dispatch failure and actual physical LED wiring failure.

Use official platform/provider troubleshooting guidance. Do not label every failure 'Bluetooth permissions', force pairing/unpairing repeatedly, update bootloaders to fix host issues, or disable antivirus/firewall/SmartScreen. Do not modify privacy/trust records to skip approvals. Never scrape or commit tokens. If a driver/user action is required, explain the evidence and ask the user to perform it normally.

Check competing hosts before touching firmware. Do not reconnect the old Mac from this Windows research session. Keep the operational release command visible in documentation so the owner can move between laptops without repeated engineering intervention.

## 12. Evidence and documentation deliverables

Use docs/windows/FINDINGS_TEMPLATE.md to create one redacted report per meaningful run under docs/windows/findings/. Name it YYYY-MM-DD-short-description.md, adding a suffix rather than overwriting another run. Record baseline, hypotheses, failures, fixes, verification, outstanding risks and next actions. Append corrections when a hypothesis changes; rewrite summary to reflect final verified behaviour.

Keep raw logs/screenshots locally in .backups/windows/ (ignored). Sanitize before sharing/committing. Do not commit usernames, exact home paths, MAC addresses unnecessarily, device inventories, prompt content, provider session IDs, secrets or full environment dumps. Avoid unbounded logs; redaction must happen before writing committed excerpts. Board public label first clawdy is needed to reproduce setup; secrets are not.

Update INSTALL.md, docs/COMPATIBILITY.md, docs/PROVIDERS.md, docs/TESTING.md, docs/LAPTOP_HANDOFF.md, AGENTS.md and CHANGELOG.md to match implementation and evidence. Create a Windows installation/troubleshooting guide with actual tested commands, prerequisites, startup/release/rollback steps, required user permissions and known limitations. Do not remove Mac installation instructions or mark all providers verified based on one adapter.

Record exact firmware/host source commits used during tests. Windows support is initially 'implementation in progress' and becomes 'verified on <tested Windows profile>' only after native BLE delivery and real provider acceptance. Packaging/signing, clean-machine customer installation and USB power qualification are separate gates.

## 13. Commit, push and handoff

The owner authorizes implementing this Windows support, documenting findings and committing/pushing related project changes. Stage only this task's files; inspect diffs for secrets/unrelated edits. Run applicable checks, commit with an accurate summary, and push the implementation branch. Prefer a reviewable PR when substantial platform changes warrant it; attach any created PR to the task. Do not merge or publish a signed/consumer release based on assumption. If the owner explicitly asks for main, honor that after required verification.

Final delivery should state: what is installed and physically verified; exact install/update/status/release commands; provider/platform coverage; startup/reconnect results; tests passed and not run; known limitations; redacted findings path; commit/branch/PR; and any specific remaining user action. Do not claim 'Windows ready' if this is only documentation or mocked tests.

Begin now by reading the repository, inspecting the actual Windows environment, and recording baseline findings. Then implement and test the smallest complete native Windows path.

Provider lists in exact-label commands are examples: after detection, ask the user which supported apps to configure and pass only that approved list. Use `--onboard` for a new buyer unit; never fall back to USB runtime.
