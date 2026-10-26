# Private macOS menu-bar candidate — 26 October 2026

Owner authorized testing, committing and pushing the Mac virtual companion, then
starting a Windows counterpart. The source is a private prototype; no release,
notarized installer, startup registration or hardware installation is included.

A fresh isolated ad-hoc-signed bundle compiled with the installed Swift toolchain.
235 integrated Python tests passed. Native host, attention real-window fixture,
renderer model/offscreen acceptance, small/full-pipe protocol tests and the
menu-only18-second host-pause/stalled-collector recovery fixture passed. The
owner previously confirmed exact local Codex Open chat navigation in this revision
line. Actual VoiceOver speech, fullscreen/hotplug, clean installation and long
native UI uptime are still separate acceptance gates. The product illustration
is temporary; a real owner toy photo remains pending.

Read-only audit caught an initial optional-renderer snapshot which bypassed the
existing chat-ID sanitizer. All initial/steady/test snapshot messages now use
one rendererSnapshot constructor, with an encoded-wire regression proving route
IDs are absent. Routing stays in the collector/menu-host memory path. No live
physical board or provider hook was changed during this verification. Existing
user trial stayed running while disposable fixtures were tested.

A macOS CI job now builds the native sources and runs hardware-free native
fixtures. This does not publish an app or establish native Windows acceptance.
Windows planning/implementation starts only after this Mac source push, in its
own bounded assignments, with no implication of release readiness.

Initial GitHub checks built the native Mac app successfully. Python3.12 jobs
exposed one test assumption: newer JSON parsers decode a deeply nested but
syntactically valid non-object frame where Python3.9 raises RecursionError. Both
paths already return unknown confidence with no activity. The regression now
asserts those safety properties and accepts the appropriate disconnected/uncertain
classification instead of depending on the interpreter's recursion limit.
