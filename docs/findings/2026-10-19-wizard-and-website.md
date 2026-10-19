# Wizard presentation and accurate website preview — 19 October 2026

The owner authorized testing, committing and pushing all prepared project work.
The existing private-release policy remains in effect: no installer or website
redesign was published publicly, and no hardware setup was run.

Daniel polished the terminal wizard into five phases with Clawdy branding,
optional TTY-aware colour, plain/piped and NO_COLOR fallbacks, safe display of
nearby-device names, and distinct installed/verified/pending states. Dry-run
remains offline. Existing naming, identity, permissions and confirmations remain.

Rafael rendered the actual unchanged 45 mm integrated model into a transparent
PNG: rectangular terracotta body, four legs, black eyes and the 66 mm black post.
No AI-invented geometry, CAD export or modification to the independent mascot
repository was used. Colour/finish is illustrative; image fidelity is not proof
of production fit or readiness.

The private site/ redesign replaces the generic rounded mascot illustration with
that model render, a cream/terracotta visual system, responsive layouts, signal
preview controls, a setup walkthrough, copy-command interaction and compatibility
information. It makes no public installer or checkout available. The working QR
site remains unchanged at its original URL.

Browser checks covered desktop, 390-pixel mobile layout with no horizontal
overflow, image load, attention preview and command-copy feedback. Software
checks cover the complete regression suite, docs, whitespace and the rebuilt
private bundle. Native Windows, clean-customer onboarding, physical persistence
and ESP32 target compilation/qualification remain pending as previously recorded.

Commit scope includes the prior prepared onboarding/protocol/hook fixes and OLED
phrase iteration, now authorized by the owner. Generated output/, local config,
logs, backups, release ZIPs and the independent mascot Git checkout are excluded.

Final local validation: 138 hardware-free tests passed in 6.474 seconds.
The customer bundle was rebuilt after wizard changes. Local documentation links
and whitespace checks passed; browser console reported no errors. Publication
remains separate from this private commit/push.

The first hosted run passed Mac/Linux but exposed a Windows pipe-read deadlock
in the observer and three tests assuming Unix paths. That run was cancelled.
The observer now uses POSIX readiness polling and Windows PeekNamedPipe/ReadFile,
with no background stdin reader. Tests cover empty/partial pipes, EOF, size
bounds, CRLF handling and native paths. All 143 integrated tests passed locally
after the fix; the follow-up push receives a fresh hosted run. Runtime observer
copy and the private customer bundle were refreshed without starting the bridge
or connecting hardware. Native Windows BLE/provider acceptance is still pending.
