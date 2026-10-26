# Virtual Clawdy · private Windows prototype

A first WPF/Win32 tray prototype, targeting .NET 10. This is separate from the
existing [Windows physical-device companion](../../docs/windows/README.md).
**Native Windows UI acceptance is pending.** macOS cross-compilation and portable
checks do not establish Windows focus, DPI, accessibility or Explorer behavior.
Keep source/bundles private; this is unsigned and is not a customer installer.

The app owns one notification-area icon and one Python collector. Default OBS
reads only the already-running bridge at `127.0.0.1:8765`; it does not start that
bridge. Explicit demo mode needs no provider, API key or device. Starting this app
never installs hooks, requests Bluetooth access, flashes hardware, alters security
settings, registers startup or enables a background service. Ordinary browser AI
chats are not tracked. Leave a released physical laptop released.

## Build on native Windows

Requirements: .NET 10 **SDK** for building, native Python 3.9+ with the `py -3`
launcher (or an explicit interpreter path), and normal access to official .NET
restore sources. No third-party NuGet UI library or Python package is required.
Use normal company IT approval for blocked downloads/execution; do not bypass
PowerShell policy, SmartScreen, antivirus, network or filesystem restrictions.

```powershell
# From the repository root; runs a build, not an installation or UI launch.
.\desktop\windows\build.ps1

# The framework-dependent build needs the .NET 10 Windows Desktop Runtime.
& "$env:LOCALAPPDATA\ClawdyPrototype\Build\publish\win-x64\Clawdy.Windows.exe"
# ARM64 defaults to the win-arm64 directory instead.
```

The script keeps output/intermediates in the local user cache. Select architecture
with `-Runtime win-arm64` or `-Runtime win-x64`; `-Output` selects a different
private destination. It does not install the SDK/runtime/Python. Do not lower OS
security settings to run this private build. Quit the app before replacing it.

```powershell
# Deliberate simulated activity, no loopback status connection.
& "$env:LOCALAPPDATA\ClawdyPrototype\Build\publish\win-x64\Clawdy.Windows.exe" --demo

# Optional installed interpreter, with spaces handled as a literal argument.
& "$env:LOCALAPPDATA\ClawdyPrototype\Build\publish\win-x64\Clawdy.Windows.exe" --observe --python 'C:\Path To Python\python.exe'
```

Only one prototype instance per logged-in Windows session is admitted. If it is
already open, use its tray menu to switch OBS/demo or quit. OBS can legitimately
show disconnected on a machine without the separately installed physical bridge.
Do not install that companion just to obtain a demo.

## Intended interaction and boundaries

- Three native horizontal traffic lights: input-needed blinks red, error is solid
  red, work amber, reported ready green; idle/unknown/disconnected have no active
  lamp. Reduce Motion uses static input red. WIP/apps appear in tooltip/card;
  Windows' icon slot does not provide the Mac's adjacent menu-bar text.
- Hover previews a compact anchored card, with delayed entry/exit. Left click
  opens it; keyboard selection offers keyboard focus. Right click exposes OBS,
  demo, Reduce Motion, Retry and Quit. Passive presentation requests no activation.
- Input/error episodes request a single expansion with retention/dismissal policy.
  Monitor work-area/DPI conversion and Explorer `TaskbarCreated` recovery are
  implemented, awaiting actual mixed-DPI/taskbar/restart acceptance. Every automatic
  expansion goes through the host's active-session/notification-state gate, including
  after an anchor is known. Denied episodes are consumed without a deferred popup.
  The source uses `GetDpiForWindow` on its invisible, nonactivating HWND at the tray
  anchor, rather than `GetDpiForMonitor` from a per-monitor-aware thread. Screen DIP
  conversion and WPF cross-monitor repositioning still require actual mixed-DPI
  evidence; successful compilation does not establish correct placement.
- App actions require a user click. Exact chat actions require a registered
  `codex` protocol and a validated host-only local Codex route. The launcher builds
  the fixed URI locally; no backend URL, command, prompt or arbitrary path is run.
  Registration is not proof of correct destination or account access. Codex/Cursor
  app actions require their registered schemes. Claude/Gemini CLI fall back to
  **Open Terminal**, which does not resume or select a particular terminal chat.
- Snapshot counts are reported working **sessions**, not OS processes. Only Y
  records contribute working-app indicators. Model names are not inferred.
  Legacy records remain `reported`, with session liveness unconfirmed. A successful
  poll cannot establish provider freshness. The shared collector excludes legacy
  anonymous Codex process-fallback records without clearing the bridge registry.
- Host presentation becomes unknown at three seconds without an accepted snapshot
  and disconnected at ten; counts/apps/actions clear. Replayed revisions cannot
  refresh liveness. After a stalled collector, only its owned process is restarted.
  Three automatic restarts (1/2/4 seconds within five minutes) precede paused
  recovery; Retry resets that in-memory budget. No persistent recovery/service is
  installed. A deliberate quit closes the icon/card and stops its collector.
  The watchdog runs independently of WPF's dispatcher. Source generations reject
  old-mode frames, and concurrent Start/Dispose cannot create extra collectors.
- Default `py` is first resolved to its actual Python executable through a bounded
  isolated, UTF-8 preflight (3-second read/exit budget), then the collector launches
  directly. Cleanup targets only the owned process tree; it never searches for
  unrelated Python/bridge processes. Explicit `--python` should name a real Python
  interpreter. Kill-on-host-crash Windows Job Objects are not implemented; a hard
  host kill plus an unresponsive child remains a native recovery gate. Normal
  broken-pipe exit and permission-denied descendant cleanup are not guarantees.
- Closing this app leaves the physical bridge and unrelated providers alone.
  Removing its private build/cache removes the prototype; it creates no startup
  entry. Forced termination, OS shutdown and denied process-control need native
  acceptance; no unlimited uptime/cleanup guarantee is made.

Routing IDs stay in private host/card memory, not diagnostic output or reports.
This Windows prototype has no separate renderer process, authenticated ingress,
installer, update/rollback flow or production signing. Its shared legacy status
source is unauthenticated loopback; do not call it an authenticated backend.

## Checks that do not claim native UI acceptance

```powershell
dotnet run --project desktop/windows/ProtocolChecks/Clawdy.ProtocolChecks.csproj
dotnet run --project desktop/windows/Validation/Clawdy.PolicyChecks.csproj
dotnet run --project desktop/windows/RuntimeChecks/Clawdy.RuntimeChecks.csproj -- --python python
# Windows-only isolated card fixtures: fake actions, no collector or tray.
dotnet run --project desktop/windows/Validation/UiChecks/Clawdy.UiChecks.csproj -c Release
dotnet run --project desktop/windows/RuntimeChecks/Clawdy.RuntimeChecks.csproj -- --python python
python -m unittest discover -s tests -v
python scripts/check_docs.py
```

Protocol checks cover frame/schema bounds, duplicate fields, count/app summaries,
confidence, stale/lost presentation and capped recovery. Policy fixtures cover
attention retention, dismissal, action validation and privacy. They can run on
macOS/Linux using .NET 10. WPF itself cannot execute there. A cross-build may use
`dotnet build desktop/windows/Clawdy.Windows.csproj -p:EnableWindowsTargeting=true`
with a private `--artifacts-path`; it is compile evidence only. Native Windows
publishing selects a Windows runtime identifier and produces its executable.

Runtime checks launch the **actual shared collector** with `-S -u --demo`, then
isolated synthetic children for crash loops, hangs, equal-revision replay,
malformed/oversized/changed-instance frames, a stderr flood, a 10,000-frame burst,
rapid source changes and launcher-descendant cleanup. Fixture recovery delays and
watchdog deadlines are shortened; production timing and native UI acceptance are
separate. No provider, bridge, Bluetooth worker or UI is launched. On macOS pass
`--python /usr/bin/python3`; the test never assumes an installed Windows launcher.

Remaining gates: actual Windows 11 x64/ARM64 installation/execution, UI Automation
and screen-reader behavior, hover/click delivery, keyboard/foreground preservation,
tray overflow, Explorer restart, taskbar placement, multiple monitors/mixed DPI,
lock/sleep/wake, Reduce Motion/high contrast, action destinations, real trusted
provider concurrency, resource measurement and 24/72-hour native soaks. Record
passed/failed/blocked/not-run evidence using the
[findings template](../../docs/windows/FINDINGS_TEMPLATE.md). Existing Mac evidence
and the separate physical Windows bridge do not clear these gates.

## Platform references

Consulted 26 October 2026: Microsoft's [notification area guidance](https://learn.microsoft.com/en-us/windows/win32/shell/notification-area)
(`Shell_NotifyIcon`, version 4, icon rectangles, DPI and `TaskbarCreated`),
[non-Windows targeting](https://learn.microsoft.com/en-us/dotnet/core/tools/sdk-errors/netsdk1100),
[window DPI](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getdpiforwindow),
[owned process termination](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.kill?view=net-10.0),
and [Windows .NET installation](https://learn.microsoft.com/en-us/dotnet/core/install/windows).
API implementation is not evidence that the owner has accepted these behaviors.
