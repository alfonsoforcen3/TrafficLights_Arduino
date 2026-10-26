# Menu-bar recovery hardening — 2026-10-21

Owner reported the virtual Clawdy in the Mac menu bar went off after restarting
ChatGPT and subsequently recovered. This report concerned the native virtual
app, not physical LEDs. The existing native host remained alive for over
18 hours; its collector had restarted shortly before inspection. This launch
had diagnostics disabled and stderr=/dev/null, so the exact incident cause
cannot be reconstructed from logs. One host/one collector and no renderer were
observed. The existing loopback status server answered normally at inspection.

## Reproduced regression

An isolated menu-only --demo --ephemeral host was started by
`python3 desktop/macos/test_lifecycle.py --recovery-only`. Its own host process
was SIGSTOPped for 18 seconds while its collector remained alive, then resumed.
The previous installed build falsely declared snapshot-timeout, terminated the
healthy collector and launched a replacement. The regression assertion failed
as intended. The test cleaned up its own processes. The owner's visible trial,
ChatGPT, physical boards, hooks, bridge and Bluetooth were untouched.

## Scope

This is a host scheduling/recovery regression, consistent with a temporary
loss of status but not proof that it caused the owner's specific incident.
The collector remains a read-only poller of an existing local companion.
Backend loss must still clear working counts and colours; recovery must not
invent fresh provider state or show cached green. No public release, commit,
startup registration, board connection or physical firmware change is included.

## Correction

Native watchdog timing now distinguishes a main-loop scheduling gap (>5s) or
wake from child progress loss. It grants one normal watchdog interval (10s for
renderer, 15s for collector) for fresh input after that gap, while invalidating
old status immediately. Received frames retain their pipe-read timestamps, so
processing queued data late does not falsely renew liveness. Failure immediately
publishes a disconnected menu state rather than waiting for another timer tick.

Manual and automatic child retries use generation/deadline tickets. Superseded
callbacks cannot launch a child, sleeping blocks new child launches, and wake
services the current due retry without erasing safe-mode budgets. Really stalled
children remain subject to bounded restart/backoff and safe mode. No singleton,
startup, permissions, hook, firmware or collector protocol change is included.

## Validation and local refresh

The same live menu-only recovery fixture PASSed on the correction: the healthy
collector survived the 18-second host pause with no replacement; subsequently
freezing the owned collector caused exactly one replacement, no renderer, and
complete fixture child cleanup. Native host self-test and renderer self-test
PASS; 224 Python tests PASS. Documentation links and whitespace checks PASS.
Native injected checks also cover wake clearing old status, pending retry
supersession/deadlines, sleep blocking new launches, and original read timestamps.

The corrected ad-hoc signed bundle replaced the private local trial, with the
previous bundle retained and SHA256 metadata updated in trial-build.json.
New host PID79153/collector79156 were running in OBS, with no renderer. The
bundled observer read one identified working coordinator turn. CUA launch again
returned a status-only AX timeout despite the successful process launch; visual
menu confirmation after this refresh remains unobserved. No actual ChatGPT
restart or OS sleep was triggered during this turn. Those exact user-visible
paths remain acceptance gates, as do extended native UI soak and release gates.
No scheduled job was re-enabled and no commit/push was performed.
