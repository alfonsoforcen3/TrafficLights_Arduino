# Windows Virtual Clawdy candidate — 2026-10-26

Private WPF/Win32 tray implementation on `codex/virtual-clawdy-windows`.
This report records integration on Apple Silicon macOS, not Windows laptop
acceptance. The virtual companion is independent of the physical BLE installer.

## Implementation and audit

The candidate includes horizontal traffic lights, WIP/provider detail, a branded
hover/attention card, a minimum 20-second recent-attention hold, keyboard controls,
reduced motion, guarded exact local Codex chat actions and explicit app/Terminal
fallbacks. Demo does not connect to a bridge or launch provider actions. OBS reads
only an existing loopback bridge. No hooks, startup, device or service installation
is performed. The image is a Clawdy illustration, not a toy photograph.

The audit fixed automatic expansion bypassing the host's notification gate,
repeated action-click admission, retained live actions crossing into Demo,
collector mode-generation races, UI-thread-dependent hang detection, and
idempotent shutdown. The host now resolves the Windows launcher to the actual
Python interpreter before starting the collector, bounds resolver output/time,
and cleans up only its owned process tree. Tray DPI uses its own invisible window
instead of GetDpiForMonitor; mixed-display placement still needs native testing.
Destinations use a pure allowlist; the backend supplies no
executable, shell command or arbitrary URL. Notifications denied by the host are
consumed for that episode instead of reopening later after a reconnect.

## Local evidence

- Python 3.9.6 with an isolated cache venv, `bleak==0.22.3` and `pyserial==3.5`:
  `python -m unittest discover -s tests -v` — **235 tests PASS**. The first
  system-interpreter run lacked `bleak`; the isolated rerun supersedes it.
- .NET SDK 10.0.403: portable card policy/admission fixtures **PASS**. These cover
  retention, dismissal, quiet-time denial, callback generations, Demo transitions,
  route validation and redacted action diagnostics.
- Portable protocol checks **PASS**: schema/frame bounds, duplicate fields,
  confidence, count/app summaries, stale/disconnected presentation and restart
  budget. No registry, provider or hardware call is exercised.
- Portable process checks **PASS** against the actual shared Python demo collector
  and isolated fixtures for crashes, hangs, replayed revisions, malformed/oversized
  output, changed instance, stderr flooding, burst coalescing, rapid mode changes,
  concurrent start/disposal and missing interpreter. Fixture recovery delays are
  shortened; production timing is not changed by those tests.
- Release cross-publish for **win-x64 and win-arm64 PASS**, with warnings treated
  as errors. Both PE architecture headers, desktop-runtime contracts and exact
  copied collector sources were checked; test fixtures are absent from packages.
  Publishing is compile/package evidence, not UI acceptance.
- Full local documentation-link check PASS.

## Automated Windows CI evidence

[Checks run 40386324014](https://github.com/alfonsoforcen3/TrafficLights_Arduino/actions/runs/40386324014)
passed all six jobs for source commit `c2ffb2b9839066761d99aba9b9351694b261f9b8`.
The Windows runner passed policy/protocol checks, all lifecycle fixtures using
both direct Python and the default `py` launcher, and the real WPF card fixtures
with synthetic events/fake launchers. Windows-native publishing passed for
win-x64 and win-arm64; Arm64 execution remains untested. The Python matrix on
Windows/macOS/Linux and native Mac fixtures also passed.

The WPF fixtures rendered the actual card and bundled illustration and exercised
hover dwell/gap/exit, denied/allowed host notification gates, retained B-to-G
actions, latest WIP, Demo/keyboard Escape, single-flight/failure/exception/stale
completion paths and shutdown. They did not launch providers, create a tray host,
connect a bridge or access hardware. These runner results do not qualify a
Windows laptop profile or any remaining manual gate below.

Reproduce the portable checks using the three projects under
`desktop/windows/Validation`, `ProtocolChecks`, and `RuntimeChecks`. The last takes
`-- --python <interpreter>` and starts only its own demo/fixture children. Raw logs
and disposable binaries remain in the local cache and are not committed.

## Native laptop gates — NOT RUN

Use the [step-by-step acceptance procedure](../VIRTUAL_CLAWDY_ACCEPTANCE.md).
Each architecture needs its own evidence: Windows 11 x64 and Windows 11 Arm64.

1. Build/launch on the actual laptop with its .NET Desktop Runtime and native
   Python, including paths with spaces/non-ASCII names, absent dependencies,
   duplicate launch and clean quit. Signing, installer, updates and startup are
   not implemented by this private prototype.
2. Observe every light/WIP/provider state, hover entry/exit, keyboard/Tab/Escape,
   attention retention/dismissal and rapid-click behavior. Verify passive cards
   preserve foreground focus; test Narrator/UI Automation, reduced motion and
   high contrast. Passive outside-click dismissal in an already-foreground app
   has no global hook and remains a known parity limitation.
3. Verify Windows quiet/full-screen/session notification suppression and no
   deferred popup after the condition clears. Test overflow, auto-hide and only
   taskbar placement settings supported by the installed Windows build.
4. Exercise 100/125/150/200% scale, mixed-DPI/negative-coordinate displays,
   attach/detach and small work areas. Native placement remains unqualified.
5. With already trusted provider integration, verify actual WIP/concurrent
   providers, supported question/error/completion transitions, exact Codex chat
   delivery, and truthful app/Terminal fallback. URI registration alone is not
   destination proof. Ordinary browser chats are not supported.
6. Test owned-collector recovery on Windows, Explorer restart, lock/unlock,
   sleep/wake, explicit retry, graceful quit and forced host termination.
   No automatic restart service for the WPF host is installed. Verify no orphan
   collector, duplicate icon, unrelated process termination or bridge change.
7. Measure CPU/memory/handles and run a 24-hour native UI soak, followed by a
   separately approved 72-hour run. A collector-only soak does not qualify the UI.

Native UI, real-provider, physical BLE, clean-machine/customer packaging and
extended stability acceptance remain pending. No physical or user observation
was invented, and no Windows consumer release is claimed.
