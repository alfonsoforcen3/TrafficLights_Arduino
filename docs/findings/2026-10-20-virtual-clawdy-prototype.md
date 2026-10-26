# Private macOS island prototype

20 October 2026. Wizard hardening was committed as `290c871` and pushed.
The first hosted run failed before tests because Ubuntu 26.04 lacked Python 3.9.
`34f6514` pins that matrix entry to Ubuntu 22.04; all four jobs in
[run 39427521625](https://github.com/alfonsoforcen3/TrafficLights_Arduino/actions/runs/39427521625)
passed. The failure email referred to the earlier run, not a failed Git push.

## Prototype delivered locally

Daniel owns the standard-library Python collector and sanitized presentation
semantics; Leo owns the native menu host/shared pipe contract; Rafael owns the
renderer. Alex integrated the bundle, reviewed evidence and added native protocol
and lifecycle tests. Daniel independently reviewed native process/pipe risks.

The owner's latest visual direction supersedes the large corner mascot:
**196 × 40 pt** compact graphite island, centered six points below the active
screen's safe camera/menu work area; **252 × 66 pt** for attention/error or
explicit moving. A miniature terracotta Clawdy sits beside horizontal traffic
lights. Only bounded size transitions animate, respecting reduced motion.
There is no continuous hover/redraw timer. Returning from a monitor change
restores safe top-center placement. Exact notch/monitor behavior needs native
physical acceptance; geometry fixtures alone cannot establish it.

The host, collector and renderer run separately. Default demo data is labeled.
Optional observation only queries an already-running loopback companion; it
never starts the bridge, BLE/USB workers or provider hooks. Active legacy records
are uncertain/last-reported because the old status API lacks provider freshness.
No session IDs, prompts or arbitrary backend text enter the renderer contract.

## Verification actually performed

Reference machine: Apple Silicon, macOS 26.6.2 (25G83), Swift 6.3.2 CLI.
Compiled with Swift 5 language mode and macOS 13 deployment target. No Xcode
project or external GUI dependency is required; the deployment target does not
certify macOS 13 or Intel operation. Build instructions are in
[the prototype README](../../desktop/macos/README.md).

- **196 hardware-free Python tests passed**, including 17 collector tests.
- Native host self-tests passed: model/frame validation, ordering, stale/replay
  handling, restart budgets, 1,000-update coalescing, real-child tiny reads,
  menu-cache invalidation and invalid CLI duration handling.
- Native renderer self-tests passed: compact/expanded size, top-center/safe-top,
  negative screen origins, tiny work areas, fallback and model validation.
- Native protocol tests passed: a small ping replies before stdin EOF; a truly
  full **65,536-byte stdout pipe** cannot block main-loop EOF cleanup.
- Native lifecycle tests passed on the final island bundle: healthy demo beyond
  watchdog interval; collector crash without renderer restart; frozen renderer
  recovery with host/collector surviving; repeated crashes stop at safe mode;
  SIGTERM quit leaves no owned children.
- Light/dark compact and expanded PNGs were rendered from the actual native view
  without screen capture and visually inspected. The final bundle's local ad-hoc
  signature passes `codesign --verify --deep --strict`.
- Changed documentation links, shell/plist syntax and whitespace passed.

The first host/renderer builds both exposed buffered tiny-pipe reads, producing
false timeouts. They now use available-data/raw nonblocking reads, with real-pipe
regressions. Independent review identified synchronous renderer pong output;
the prefilled-pipe fixture reproduced a hang on the old build, and passes with
bounded nonblocking output. The initial full-vector redraw loop cost about
7–10% sampled renderer CPU and was replaced by cached/event-driven rendering.

Final integrated **16.27-second** demo sample, using process CPU-time deltas:
host 0.37%, collector 0.06%, renderer 0.25% of one core; combined peak RSS
**86.6 MiB**. No child restarts occurred. These are short, loaded-machine
observations including state changes, not a five-minute benchmark, battery
measurement, 24/72-hour soak or guaranteed resource ceiling.

Building on cloud-backed Desktop repeatedly reintroduced Finder metadata and
failed signing. Build artifacts now live under
`~/Library/Caches/ClawdyPrototype/Build/`, with only generated Finder/resource-fork
metadata stripped before ad-hoc signing. Quarantine and OS security settings were
not changed. The generated bundle and preview PNGs are not source commits.

## Pending before a readiness claim

Direct native UI automation could not acquire the status-only app (two CUA
timeouts). This is a verification limit: menu clicking, actual keyboard focus,
click-through, dragging and VoiceOver behavior are not accepted by screenshots
or source inspection. Actual camera/notch positioning, external monitor changes,
fullscreen/Spaces, lock/sleep/wake, power pressure, clean-user install, real
providers and longer soaks remain pending. No physical hardware was accessed.

Preferences and crash budgets are memory-only in this prototype; relaunching the
host resets them. No host crash supervisor, production sandbox, notarized signed
distribution, login registration, transactional updater or customer installer
is shipped. The legacy observer endpoint is unauthenticated; the narrow inherited
pipe boundary does not secure that old endpoint. No live hooks/services were
changed and no prototype source was committed, pushed or published. Test apps
were stopped after verification. Keep this a private development prototype.

## Subsequent owner trial and expanded acceptance

The owner later requested an on-Mac trial and explicitly confirmed the island
was visible. After the requested WIP/app indicators were added and tested, the
trial was refreshed and the owner confirmed both are visible. It remains running
in demo mode. See the [current acceptance record](../VIRTUAL_CLAWDY_ACCEPTANCE.md)
for 215-test integration evidence, native offscreen fixtures, working-only app
semantics, the active elapsed 24-hour collector soak and remaining readiness gates.
The earlier statement that test apps were stopped describes the earlier test
iteration, not this user-requested trial. No production readiness is claimed.
