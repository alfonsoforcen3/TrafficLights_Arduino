# Virtual Clawdy — Windows native acceptance

Private WPF/Win32 prototype checklist. The Windows app targets .NET 10 and has
separate `win-x64` and `win-arm64` publish options. Microsoft lists Windows 11
x64 and Arm64 among .NET Windows architectures, but that is runtime support, not
proof that this app works on either architecture. As of **2026-10-26, manual
Windows laptop acceptance remains pending**. Automated Windows-runner results
are recorded below. Run x64 and Arm64 as separate profiles;
a build or run on one does not qualify the other. See the [Windows prototype
README](../../desktop/windows/README.md), [macOS acceptance record](../VIRTUAL_CLAWDY_ACCEPTANCE.md), and [Windows findings](findings/2026-10-26-virtual-clawdy.md).

## Evidence rules

- Run only in a native, logged-in Windows session (not WSL). Record Windows
  edition/build, OS and process architecture, app revision, .NET and Python
  versions, display scaling/layout, date, and outcome in the dated findings
  report. Sanitize home paths, chat IDs, prompts, and logs.
- Mark every row **PASS / FAIL / BLOCKED / NOT RUN** with observed result and
  evidence. Do not count source inspection, macOS fixtures, or cross-compilation
  as Windows UI acceptance.
- This private app is unsigned and is not an installer. It has no login startup,
  updater, service, or crash supervisor for its own host. It does not install
  hooks, start the existing bridge, access hardware, or require a toy. Do not
  run the BLE physical-companion installation commands in `docs/windows/AGENT_PROMPT.md`
  or `docs/windows/INSTALL.md` to set up this virtual demo. Do not install hooks
  or stop a shared provider/bridge as incidental test setup.
- Use demo mode for UI and collector fault tests. Test OBS or provider behavior
  only when the local bridge and normal trusted provider hooks already exist and
  their use is approved. Never put private conversation data in evidence.
- Save work before manually restarting Explorer or suspending Windows. If a
  disruptive step is not safe, mark it **BLOCKED** and state why.

## 1. Preflight and build

Run in PowerShell from the repository root on the Windows machine:

```powershell
$Repo = (Resolve-Path .).Path
$OS = Get-CimInstance Win32_OperatingSystem
$OS | Select-Object Caption, Version, BuildNumber, OSArchitecture
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
dotnet --list-sdks
 dotnet --list-runtimes
py -3 --version
py -0p
```

The app requires the **.NET 10 SDK** to build and the **.NET 10 Windows Desktop
Runtime** to run framework-dependent output. It also needs native Python 3.9+
and the `py -3` launcher for its collector. Do not install anything as part of
this checklist without normal user/IT authorization; do not bypass SmartScreen,
PowerShell policy, antivirus, or network controls. If a prerequisite is missing,
mark build/run checks blocked with the exact sanitized message.

Build the native architecture. On x64 Windows:

```powershell
Set-Location $Repo
.\desktop\windows\build.ps1 -Runtime win-x64
$Exe = Join-Path $env:LOCALAPPDATA 'ClawdyPrototype\Build\publish\win-x64\Clawdy.Windows.exe'
Test-Path $Exe
```

On Arm64 Windows, use a separately installed/available Arm64 .NET 10 SDK and
Desktop Runtime, then:

```powershell
Set-Location $Repo
.\desktop\windows\build.ps1 -Runtime win-arm64
$Exe = Join-Path $env:LOCALAPPDATA 'ClawdyPrototype\Build\publish\win-arm64\Clawdy.Windows.exe'
Test-Path $Exe
```

If the app is tested as x64-emulated on Arm64, record that distinctly from the
native `win-arm64` executable. Do not treat an x64 cross-publish as native
Arm64 acceptance. Run the portable checks separately; they do not open WPF UI:

```powershell
dotnet run --project desktop/windows/ProtocolChecks/Clawdy.ProtocolChecks.csproj
dotnet run --project desktop/windows/Validation/Clawdy.PolicyChecks.csproj
dotnet run --project desktop/windows/RuntimeChecks/Clawdy.RuntimeChecks.csproj -- --python python
# Isolated Windows WPF control fixtures; fake launchers, no provider/collector.
dotnet run --project desktop/windows/Validation/UiChecks/Clawdy.UiChecks.csproj -c Release
py -3 -m unittest discover -s tests -v
py -3 scripts/check_docs.py
```

## 2. Demo tray and state behavior

Launch a disposable demo process and record its PID:

```powershell
$Demo = Start-Process -FilePath $Exe -ArgumentList '--demo' -PassThru
$Demo | Select-Object Id, ProcessName, StartTime
```

The demo timeline repeats every 46 seconds, measured from collector start. Hover
to read the tooltip and enter the card; the traffic-light icon itself does not
show adjacent text. Check each phase against the tooltip/card:

| Approximate demo time | Expected presentation |
| --- | --- |
| 0–3 s | Idle, no WIP/provider |
| 4–9 s | Working, 1 WIP, Codex |
| 10–16 s | Working, 2 WIP, Codex and Claude |
| 17–22 s | Input/attention (blinking red unless reduced motion), 1 working WIP; explicit attention action is represented, but demo must launch no app |
| 23–28 s | Error (steady red), 1 working WIP; demo must launch no app |
| 29–34 s | Working, 1 WIP, Claude |
| 35–41 s | Ready, 0 WIP |
| 42–45 s | Idle, 0 WIP |

Repeat the cycle at least once. Verify reported app indicators come only from
working sessions, are app names rather than model guesses, and update without
stale WIP. Confirm demo is visibly labeled, and clicking any demo action cannot
launch an application.

## 3. Hover, attention, routing, focus, and accessibility

- Hover the tray icon; verify the card opens after the intended delay. Move the
  pointer across the icon/card gap and into the card; it must stay open. Leave
  the card and verify it closes after the exit delay. Click the icon to open
  explicitly and use the card close button.
- Test one automatic attention/error expansion per episode. It must not take
  foreground focus. Dismiss it, let the episode clear, and confirm a later new
  episode can expand. Automatic expansion is subject to Windows notification/
  full-screen state; verify it is suppressed when Windows says notifications
  are unavailable, while explicit **Show status** still works. A quiet-time
  auto-show bypass and repeated-action guard were reported under repair for the
  current candidate; do not mark these checks PASS until that fix is integrated.
- On a real, already-configured status source only, use a genuine local Codex
  input/attention event. If the Codex protocol is registered and the chat is
  verified, click **Open chat** and visually confirm it opens that exact local
  conversation. Do not include its ID or title in the report. With an
  unsupported/unverified route, confirm the explicit **Open Codex** fallback;
  Claude/Gemini CLI actions open Terminal without selecting or resuming a chat;
  Cursor uses its registered protocol when available. No guessed URI or unrelated
  chat may open. Never use the demo to claim route acceptance.
- Allow a real attention/error report to clear. Its action must remain visible
  for at least 20 seconds, say it is recent, and show current WIP. Hover/keyboard
  interaction keeps the recent card available until exit/dismissal. Double-click
  an action once and verify at most one launch; retry only after observing the
  first result.
- Leave another ordinary app in the foreground. Hover and automatic expansion
  must leave that app and keyboard focus unchanged. Open the tray context menu,
  choose **Show status** by keyboard, then check visible focus, Tab order, Escape,
  close, and return to the prior app. A click/keyboard-opened card may activate
  intentionally; passive hover may not.
- Inspect the card with Windows UI Automation (for example Accessibility
  Insights if already available) and Narrator. Check accessible name/role/help
  for heading, state, WIP, provider names, confidence/demo, close and action
  buttons. Mark Narrator/inspection blocked if the utility is unavailable; do not
  install tools without authorization.
- Turn off **Settings → Accessibility → Visual effects → Animation effects**;
  verify expansion motion is removed/reduced while content still updates. Check
  a high-contrast theme if available, and restore the user's original settings.

## 4. OBS and preconfigured provider checks

OBS means read-only observation of the **already-running** bridge at
`127.0.0.1:8765`; the virtual app never starts it. Check without changing it:

```powershell
Test-NetConnection 127.0.0.1 -Port 8765 -InformationLevel Quiet
```

If false, launch OBS and verify disconnected/unlit status. Do not start the
physical bridge merely for this test. If true and use is approved, launch OBS:

```powershell
$Observed = Start-Process -FilePath $Exe -ArgumentList '--observe' -PassThru
```

If the Python launcher is not the intended interpreter, identify an existing
native Python path with `py -0p`, then pass it using a quoted argument. For a
path containing spaces, for example:

```powershell
$Python = 'C:\Program Files\Python39\python.exe' # replace with a path from py -0p
$Observed = Start-Process -FilePath $Exe -ArgumentList @('--observe', '--python', ('"{0}"' -f $Python)) -PassThru
```

Do not copy the developer's Python path. The `--python` option selects an
existing interpreter; the prototype does not install Python or its dependencies. Confirm a successful local poll does not label
legacy session status provider-fresh. On a fresh/stale/lost connection, verify
stale state after about 3 seconds, disconnected after about 10, and a fresh
snapshot before returning to a current state.

Only if the user's ordinary trusted provider hooks and bridge are already
configured, test a normal Codex turn and completion and confirm WIP/provider
summary. Do not install or alter hooks or trust to make this pass. A real
attention route requires a separately observed, genuine local Codex
input/error event and a verified local route; ordinary browser chats are not
supported. Record provider checks as **NOT RUN** if those prerequisites are absent.

## 5. Display, tray, Explorer, loss, and lifecycle

- **Scale/DPI:** test at the machine's normal scale and, when available, 100%,
  125%, 150%, and 200%. Move the card between displays with different scaling;
  verify no clipping and that it stays in the correct taskbar work area. Record
  actual settings and displays; don't emulate a second architecture by changing
  DPI. The app manifest requests PerMonitorV2, but this remains a native test.
- **Edges/work area:** test the icon/card at the system tray and near each screen
  corner, small work areas, autohiding the taskbar, negative-coordinate monitor
  layouts, and display attach/detach when safe. Windows 11 taskbar placement
  options vary by build/update rollout: test top/left/right only if the supported
  setting is present on that machine; otherwise record N/A and test the available
  placement. Do not edit registry keys or use third-party taskbar tools.
- **Overflow:** test when the Clawdy icon is shown/hidden under the tray overflow
  chevron. Its tooltip, hover, click, and context menu must remain reachable.
  Also exercise long phrases/provider lists and multiple attention actions; no
  clipped or unreachable controls.
- **Explorer restart:** save work, use Task Manager → Processes → Windows Explorer
  → Restart, then verify exactly one tray icon returns and status resumes. Do not
  use `Stop-Process` against Explorer. Mark blocked if restarting it is unsafe.
- **Collector crash/recovery:** only in disposable demo mode, identify the
  collector as a descendant of this exact app PID and verify its command line
  contains this build's `collector\virtual_clawdy.py` and `--demo`. If ownership
  is ambiguous, do not terminate anything. The guarded PowerShell below lists
  only descendants; inspect its output and abort unless exactly one process is
  the demo collector. Then terminate only that PID and verify the tray stays
  responsive and observes the documented 1/2/4-second restart sequence. Repeat
  the guarded check for each deliberate failure; after three automatic restarts
  in five minutes, verify recovery pauses and tray Retry resumes it. Never kill
  Python by process name or a provider/bridge process.

  ```powershell
  $AppPath = (Get-Item $Exe).FullName
  $Hosts = @(Get-CimInstance Win32_Process -Filter "Name='Clawdy.Windows.exe'" |
      Where-Object { $_.ExecutablePath -eq $AppPath })
  if ($Hosts.Count -ne 1) { throw 'Expected exactly one host at this build path; abort.' }
  $HostPid = [uint32]$Hosts[0].ProcessId
  $ProcessSnapshot = @(Get-CimInstance Win32_Process)
  function Get-OwnedDescendants([uint32]$ParentId, [object[]]$Snapshot) {
      $Children = @($Snapshot | Where-Object { $_.ParentProcessId -eq $ParentId })
      foreach ($Child in $Children) {
          $Child
          Get-OwnedDescendants ([uint32]$Child.ProcessId) $Snapshot
      }
  }
  $OwnedDemo = @(Get-OwnedDescendants $HostPid $ProcessSnapshot | Where-Object {
      $_.CommandLine -and $_.CommandLine.Contains('\collector\virtual_clawdy.py') -and
      $_.CommandLine -match '--demo(?:\s|$)'
  })
  $OwnedDemo | Select-Object ProcessId, ParentProcessId, Name, CommandLine
  if ($OwnedDemo.Count -ne 1) { throw 'Expected exactly one owned demo collector; abort.' }
  Stop-Process -Id $OwnedDemo[0].ProcessId -Force
  ```
- **Backend loss:** do not stop the shared provider bridge. Use a disposable
  isolated backend fixture only if the test harness for it is available; otherwise
  mark induced OBS-backend loss **NOT RUN**. Real disconnected status can be
  checked without disruption when the bridge is already absent. Verify stale and
  disconnected presentation and no cached actions on any naturally occurring
  outage.
- **Sleep/wake and session lock:** save work, put the laptop to sleep and resume;
  separately lock/unlock if practical. Verify stale/disconnected data is not
  shown as current, the app remains responsive, and no duplicate collector/icon
  appears. If not safe to sleep, mark blocked. No power settings are to be changed.
- **Host exit/crash:** this prototype has no supervisor/restart service for its
  own WPF host. A host crash is not expected to auto-relaunch. Verify the app
  process exits; check whether its collector is also gone, and report any orphan
  as a failure. Manually relaunch the app to recover. Do not add a startup task.
- **Cleanup:** quit from the tray menu, then check the exact executable is gone:

  ```powershell
  Get-CimInstance Win32_Process -Filter "Name='Clawdy.Windows.exe'" |
      Where-Object { $_.ExecutablePath -eq $AppPath } |
      Select-Object ProcessId, ExecutablePath
  ```

  Confirm its collector is gone, tray icon/card disappear, and no startup entry,
  hook, service, hardware bridge, or unrelated process was installed/stopped.
  Deleting the private build cache is separate and is not part of this test.

## 6. Soaks and results

Run a **24-hour demo soak** first, then a separate **72-hour soak** only if the
24-hour run is clean and the owner approves leaving the private app running.
Record start/end, interruptions, observed state, process CPU/RSS/handles, icon
presence, unexpected restarts, and cleanup. The demo needs no real provider,
hardware, startup entry, or AI request. Sample at start, 1 hour, 8 hours, and end;
use the PID returned by `Start-Process` and verify its executable path each time:

```powershell
Get-Process -Id $Demo.Id -ErrorAction Stop |
    Select-Object Id, CPU, WorkingSet64, Handles, StartTime
(Get-CimInstance Win32_Process -Filter "ProcessId=$($Demo.Id)").ExecutablePath
```

Do not terminate processes by a broad name filter. A single screenshot or short
launch does not pass an elapsed soak. Keep native
interaction, architecture, provider, and elapsed-time results in separate rows.

| Windows-native check | Result |
| --- | --- |
| Windows 11 x64 build, launch, and demo UI | NOT RUN |
| Windows 11 Arm64 native build, launch, and demo UI | NOT RUN |
| Demo state/WIP/provider timeline and no-action rule | NOT RUN |
| Hover gap, single-episode auto-open, 20-second retention | NOT RUN |
| Exact verified Codex chat and unsupported-provider fallback | NOT RUN |
| Passive focus, explicit keyboard path, accessibility/Narrator | NOT RUN |
| Reduce Motion and high contrast | NOT RUN |
| Tray overflow, work-area edges, scale/mixed DPI, display changes | NOT RUN |
| Explorer restart | NOT RUN |
| OBS with bridge absent and already-running (no induced outage) | NOT RUN |
| Existing trusted real-provider turn/concurrent sessions | NOT RUN |
| Owned demo collector restart budget and Retry | NOT RUN |
| Sleep/lock/wake, host/collector cleanup | NOT RUN |
| 24-hour and 72-hour native demo soaks | NOT RUN |
| Clean quit; no startup/hooks/services/hardware side effects | NOT RUN |
| Portable protocol/policy tests on Windows | PASS on isolated CI runner; laptop profile NOT RUN |

## Automated Windows-runner evidence

At source revision `c2ffb2b9839066761d99aba9b9351694b261f9b8`,
[Checks run 40386324014](https://github.com/alfonsoforcen3/TrafficLights_Arduino/actions/runs/40386324014) passed all six jobs:

- Windows policy/protocol fixtures and 13 lifecycle groups, repeated with direct
  `python` and default `py` launcher resolution.
- Windows WPF fixtures using the actual card, real dispatcher and render bitmap,
  synthetic control/pointer events and fake launchers. The bundled illustration,
  hover timers, notification gate, recent actions, Demo, Escape, repeated-click
  admission, failure/stale callbacks and idempotent shutdown were exercised.
- Native Windows publishing for win-x64 and win-arm64. Arm64 execution was not
  performed on an Arm64 Windows machine.
- Python regressions on Windows/macOS/Linux, documentation checks and native
  macOS build/fixtures.

This is real automated Windows execution, not a macOS simulation. It does not
prove physical pointer delivery, foreground focus, OS notification-state changes,
actual tray/Explorer behavior, Narrator, mixed-DPI displays, real chat recipients,
provider integrations, forced-host cleanup or extended native UI stability. The
manual laptop rows above retain their explicit NOT RUN status.

## Platform references and interpretation

Consulted 26 October 2026. Microsoft's [.NET Windows installation matrix](https://learn.microsoft.com/en-us/dotnet/core/install/windows)
lists Windows 11 x64 and Arm64 runtime/SDK support; this does not certify this
application. The app manifest declares PerMonitorV2; Microsoft's [GetDpiForMonitor
documentation](https://learn.microsoft.com/en-us/windows/win32/api/shellscalingapi/nf-shellscalingapi-getdpiformonitor)
says that API should not be used from a per-monitor-aware calling thread. The
current tray source declares PerMonitorV2 and calls GetDpiForMonitor, so mixed-DPI
placement is a priority check and any defect should be recorded for engineering
review, not explained away by the manifest. Microsoft taskbar position controls
are rollout/build dependent; see [Windows taskbar customization](https://support.microsoft.com/en-us/windows/experience/personalization/customize-the-taskbar-in-windows).

Portable protocol/policy fixtures and a successful cross-publish prove only the
code they exercised. They do not qualify native Windows UI, architecture
execution, focus, accessibility, tray placement, Explorer recovery, providers,
sleep/wake, cleanup, or a soak.
