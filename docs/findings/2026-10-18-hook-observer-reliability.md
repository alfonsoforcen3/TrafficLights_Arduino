# Hook observer reliability — 18 October 2026

## Symptom and evidence

The owner reported sessions sometimes ending before delivery. The CEO also
sent a final answer while delegated work was pending. That early answer was a
coordination error; no hook evidence establishes it as the cause.

Installed Codex and Claude traffic-light commands pointed into the Desktop
checkout. macOS marked traffic.py compressed/dataless, and ordinary cat/sed/Python
reads stalled before executing handler logic. A terminal process listing and
open-file inspection confirmed blocked source reads; the file was a regular
file, not a FIFO. Later hydration recovered. Default shell choice was ruled out
when bash reads also stalled. This is a concrete timeout risk independent of
provider permissions or the model's decision to finish.

The old observer also read stdin until EOF, imported serial eagerly, could open
a broad-match USB device when the bridge was absent, and wrote logs inside the
checkout. These operations are inappropriate on a best-effort lifecycle path.

## Fix boundaries

- Use a copied observer in the per-user local runtime, not cloud-backed source.
- Bound stdin and loopback communication; hardware/bridge absence must fail open.
- Emit only the provider's neutral output, with no Stop continuation/block policy.
- Do not directly probe USB, connect BLE, mutate permissions, read transcripts
  or write source-tree logs from a lifecycle observer.
- Type-check hook ownership and schema, preserve unrelated/null fields, respect
  disabled policies and back up settings before an existing-command migration.
- Coordinator must collect pending specialist results and verify integration
  before final delivery. Traffic-light hooks do not enforce task completion.

The existing-command migration copies traffic.py and changes owned commands
only. It must not create hooks, restart the helper or reconnect a released host.
Normal provider trust review is still required after path changes. Do not edit
trust stores or macOS privacy databases.

## Validation

Specialists run synthetic observer tests with malformed input, stalled input,
absent/stalled bridge, output contracts and config preservation. The coordinator
runs the integrated hardware-free suite and verifies the actual migration diff.
Real AI turn acceptance and physical Bluetooth checks remain separate; no blocked
AI task is deliberately manufactured to claim a fix.

The owner-authorized migration was applied to this Mac: 8 Codex and 9 Claude
owned commands changed to the local runtime. A comparison with private backups
verified command-only changes; no services/hardware were restarted or connected.
The copied observer was syntax-checked and matched reviewed source. Settings and
backups remain local and are not included in Git or the customer archive.
Changed paths still need normal hook trust review in the respective providers.

An early onboarding test's incomplete mock unintentionally performed an eight-
second BLE discovery with no matching toy and no connection. Fail-fast guards
and explicit mocks were added. This incident is recorded rather than counting
it as hardware acceptance. A timing-sensitive identity-cleanup unit test also
failed once at a 30 ms deadline; its timing assumptions were referred back to
the firmware specialist before final integration.

Final combined validation: **134 tests passed in 6.642 seconds**, no skips.
The first combined run hit a two-second subprocess deadline before startup was
separated from handler execution. The test now uses a bounded READY handshake
for interpreter/import startup, then retains the original two-second EOF/exit
deadline; all 12 focused observer tests and the full suite pass. Production
handler deadlines were not relaxed. Installed Codex/Claude/Cursor observer
output and zero-exit behavior were also verified with network operations mocked.
This is software evidence, not real-provider trust/dispatch acceptance.
