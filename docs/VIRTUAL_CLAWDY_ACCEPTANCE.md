# Virtual Clawdy acceptance record

Private macOS development prototype, 20 October 2026. **Not release-ready.**
Latest owner preference: menu-bar traffic lights, no floating widget by default.
Normal relaunch now observes the existing companion read-only; demo/overlay are
explicit choices. The earlier island confirmations below are historical evidence.
See [build instructions](../desktop/macos/README.md) and
[the release plan](VIRTUAL_CLAWDY_PLAN.md).

## Evidence collected

| Check | Result and scope |
| --- | --- |
| Launch on owner's Mac | Running demo launched; owner explicitly confirmed the island is visible below the camera/menu area |
| Updated visible indicators | Owner explicitly confirmed both WIP badge and app names are visible in the refreshed demo; the previous build was preserved |
| Python integration | 215 tests passed; includes 3,125 provider-state combinations, 500 malformed replies and a 10,000-poll reconnect trace |
| WIP/provider semantics | Counts Y records only; app indicators include working providers only, matching physical Clawdy; no model inference |
| Menu behavior | Detached production menu fixture validates nine targets/actions, hide/show, pause, move and motion preferences |
| Native accessibility | Real AppKit view metadata plus menu status label/value/help expose state, WIP, provider apps and demo qualification |
| Panel behavior | Offscreen native fixture validates non-key/non-main, click-through property, floating/current-desktop flags; ordering did not change foreground app |
| Placement | 280 simulated screen/state/move cases, including negative origins, safe top and tiny work areas |
| Preferences/lifecycle | Production handlers tested with injected hide, pause, reduced motion, screen changes and sleep/wake inputs; these are not actual OS transitions |
| Recovery | Tiny live-pipe frames, genuinely full output pipes, owned-child crash/freeze recovery, restart circuit breaker and cleanup tests passed |
| Animation | Finite transitions; mixed working-app rotation only every five seconds while eligible; hide/pause/sleep/move/reduced motion stop rotation |
| Short elapsed collector soak | Actual 60-second run passed, 578 snapshots and no failures; accelerated stress tests are separate evidence |

## Long-running check

An actual **24-hour isolated demo collector soak** began on 20 October 2026 at
18:09 Dubai time. Frozen source hashes and the bounded summary are under
`~/Library/Caches/ClawdyPrototype/Soaks/`; `active-soak.json` identifies the run.
No native overlay, real AI provider, hardware bridge or hook is started by this
test. The first minute recorded 61 snapshots without failures.

The scheduled follow-up **Clawdy private stability follow-up** checks this run
quietly and reports a meaningful completion, failure or required action. It
stops after a terminal result. Keep local scheduling availability distinct from
the test itself; sleep, logout or a stopped desktop app can interrupt evidence
or delay follow-up. No power settings or startup services were changed.

## Still pending

- Actual mouse click delivery through the island, real menu interaction and
  VoiceOver speech/navigation. Source flags and detached fixtures do not prove
  those user interactions.
- Actual notch geometry across supported Macs, physical monitor hotplug/DPI
  changes, fullscreen/Spaces/Stage Manager, lock and sleep/wake.
- Completed 24/72-hour native UI stability evidence and longer resource tests.
  Collector success alone cannot clear these gates.
- Real trusted provider dispatch and concurrent-session acceptance. The optional
  legacy observer remains explicitly unconfirmed because its replies cannot
  establish provider freshness.
- Clean-user packaging, production signing/notarization, sandboxing, persistent
  crash budgets and update/remove behavior for a distributable app.

The visible app now defaults to the read-only observer. Demo fixtures are labeled
and require explicit selection. These are AI application
indicators (Codex, Claude Code, Gemini CLI, Cursor), not underlying model names
or operating-system process counts. Native fixtures and background collector
tests must not replace, terminate or manipulate the owner's trial instance.
The owner-requested indicator update was tested as a separate candidate, then
the trial was refreshed once and left running. Its binary/resource hashes and
previous-build path are recorded in
`~/Library/Caches/ClawdyPrototype/trial-build.json`.

## Menu-bar observer correction

The initial observer collapsed every retained legacy state to “Unclear.” The
bridge was reachable and reporting work; the display policy hid that information.
Consistent reported states now retain their traffic-light colour. Separate
confidence is `demo`, `reported`, or `unknown`, never provider-fresh/confirmed.
The bar qualifies unconfirmed records with `?` and tooltip/accessibility text.
Loss of the backend clears counts/apps and unlights the lamps; it cannot hold
cached green. Malformed/inconsistent reports remain unknown rather than success.

218 integrated Python tests pass for this correction, including green → loss →
working recovery and confidence validation. Native menu bitmap/semantic tests
cover all states, dark/light appearance and bar-only startup. The running
24-hour collector soak uses its frozen earlier source and is evidence for that
specific baseline, not automatic acceptance of later observer/UI changes.
Input-needed has an explicit Input label and red blink using the existing
one-second host tick; errors are steady red with an Error label. Pause or Reduce
Motion makes input red static. Native phase/pixel/cache tests distinguish these
states without adding a new timer.

The final local bundle passed host/renderer self-tests and offscreen native
acceptance after this change. A real four-second default launch verified OBS,
one collector, no renderer and clean owned-child shutdown. The refreshed owner
trial is running with only host and observer collector; the previous bundle was
preserved. No bridge/service/hook or hardware configuration was changed.
The owner explicitly confirmed that traffic lights are visible in the top menu
bar and the floating island is gone.

### Phantom WIP correction — October 20

Owner reported 1 WIP while idle. Read-only inspection found an approximately
2.5-hour-old Codex process-fallback Y record. Its parent is a long-lived app
process; a later completion keyed by conversation ID cannot clear that record.
The virtual observer now excludes numeric `codex:proc_` records from count,
provider list and logical state, preserving identified chat activity. It does
not expire long-running identified turns or mutate the bridge registry.
The refreshed signed private bundle is running menu-only with one collector;
219 Python tests and native host self-test passed for this display correction.
Live observation during investigation counted the coordinator and specialist
turns; idle-after-final display has not yet been human confirmed.

Specialist review confirmed the lifecycle mismatch and added source prevention:
unidentified hook events skip delivery instead of creating process-ID sessions;
explicit RESET/CLEAR and stable IDs remain supported. Integrated full suite:
224 tests pass. Installed hook runtime is unchanged; the running virtual app
already excludes the existing legacy orphan.

### Recovery correction — October 21

Owner reported menu-bar lights going off after ChatGPT restart, then recovering.
A live isolated regression reproduced false collector restart following an
18-second host scheduling pause on the previous build. The corrected build
survives that pause, restarts a truly frozen collector exactly once and cleans
up its owned children. Native injected tests cover sleep/wake, stale queued
input and superseded retry tickets; 224 Python tests pass. The signed private
trial was refreshed locally in menu-only OBS mode. Exact owner incident cause
is unproven because that launch did not save diagnostics; actual ChatGPT
restart/OS sleep visual acceptance remains pending. See
[recovery evidence](findings/2026-10-21-virtual-clawdy-recovery.md).

### Hover and attention panel — October 21

The running private menu-bar trial now includes native hover details and one
nonactivating automatic expansion per question/error episode. Dismissal persists
through report/reconnect churn; Reduce Motion/Pause removes reveal animation.
Explicit actions open fixed provider apps/Terminal, not guessed chat links.
Separate enum-only attention targets prevent opening an unrelated working app.
The cryptic question-mark suffix was replaced by plain-language detail text.

227 Python tests, native host checks, offscreen and real-window attention
fixtures, and the live menu-only pause/stall recovery regression PASSed. Static
visual review passed. Fixtures inject production interaction handlers/fake app
launchers; human pointer, VoiceOver speech, exact chat routing, fullscreen and
long UI acceptance remain separate gates. Current trial host85877/collector85878
was confirmed running after refresh. Physical board firmware was untouched.
See [hover evidence](findings/2026-10-21-virtual-clawdy-hover.md).

### Exact attention-chat routing — October 21

Verified local Codex user chats now offer Open chat rather than only Open Codex;
up to3 simultaneous verified routes have individual numbered actions. The
collector validates bounded local Desktop metadata and sends canonical IDs only
to the host, which strips them from optional renderer data. No prompts/titles or
arbitrary backend URLs are forwarded. Unsupported/unverified targets retain
explicit app/Terminal fallback labels. 235 Python tests, native host and real-panel
fake-routing checks and live menu-only recovery fixture PASS. Local trial refreshed
and running. Actual recipient thread rendering after a real pending-chat click
remains a manual acceptance gate; fake routing tests establish the exact URI and
fixed app destination, not recipient UI state. See
[exact chat evidence](findings/2026-10-21-virtual-clawdy-exact-chat.md).

### Recent alert and branded card — October 21

Owner's first actual question test exposed a brief panel that disappeared before
click. Native UI now retains its exact-chat action for a20s minimum click window,
labels cleared status as a recent request/error, and shows current WIP. Hover/key
interaction preserves it until exit; dismissal/sleep/menu/mode/cleanup cancels.
Native rapid B→G/B→Y/offline, deadline and stale callback tests PASS, as did the
menu-only pause/stall recovery fixture. Human click acceptance remains pending.

Branded332×184 card with warm product tile and terracotta details is running.
The image is the faithful CAD illustration, NOT a physical photograph; owner was
asked to supply the actual toy photo. Bundled7state visual QA and native checks
PASS. See [retention evidence](findings/2026-10-21-virtual-clawdy-alert-retention.md)
and [branding evidence](findings/2026-10-21-virtual-clawdy-branding.md).

Owner end-to-end confirmation (October21): after the branded/retention refresh,
Open chat on the actual test-question card brought the owner to this exact
session, explicitly confirmed. Local Codex real-click routing for this scenario
is accepted. Other providers/remote hosts, actual toy photo, VoiceOver and long
native stability gates remain separately pending.
