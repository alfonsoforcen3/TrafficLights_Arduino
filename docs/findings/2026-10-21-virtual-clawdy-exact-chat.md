# Exact attention chat — 2026-10-21

Owner explicitly requested opening the exact chat rather than only the app.
The installed Codex app registers `codex` and its own thread-link parser accepts
`codex://threads/<UUID>`. No chat messages, prompts or generated answers are sent
by that navigation. Actions remain explicit-click only.

The collector resolves only B records for question state and R records for error
state. A canonical Codex UUID is eligible only when a local session metadata file
matches its filename and session_meta.id, source=vscode, originator=Codex Desktop,
and thread_source=user. Remote/unverified IDs, CLI/subagent records, malformed IDs,
URLs and path input receive no exact route. Metadata checks are bounded to the
first256KiB of the first line, max4 candidate files, max128 cached IDs with60sTTL.
No conversation body is read. At most3 distinct eligible chats are offered in the
compact panel. Multiple chats have separate numbered actions rather than silently
selecting an unrelated working chat.

Optional typed attention_chats contains provider=codex and canonical thread_id.
It is kept in the local collector/host memory path only, stripped before any
optional renderer message, and not added to diagnostics, reports or persistence.
Old snapshots without it remain valid; null/malformed/duplicate/nonred/demo routes
are rejected. The native action independently validates the UUID and constructs
the fixed scheme/host/path locally. It pins dispatch to com.openai.codex rather
than opening arbitrary provider-supplied URLs. Changes in the attention route
invalidate pending launch callbacks; WIP/phrase changes preserve button identity.

For providers without verified conversation navigation, the UI retains an honest
app/Terminal fallback. Claude Code/Gemini session IDs are not assumed to be desktop
chat links. This iteration establishes exact routes for verified local Codex user
chats, not universal provider deep links or remote-host routing.

## Verification

235 integrated Python tests PASS. Added eight metadata/routing tests cover
matching local headers, remote/CLI/subagent/mismatched records, bounded metadata,
path/URL rejection, symlink escape rejection, negative-cache expiry/size, backend
route injection and state/demo eligibility. Native host self-test PASS, including
renderer-wire stripping and invalid/null route rejection. Offscreen and real-panel
attention tests PASS with fake openers: exact URI, fixed destination, failure,
stale callback, native focus identity, multiple chats and demo no-open guard.
The bundled resolver also verified this coordinator's real local session header
using an in-memory B fixture; live bridge state was not changed.

The native open completion confirms OS handoff, not that the recipient rendered
the intended thread. No test click into a real pending chat was performed during
this turn. Installed-app parser/copy-link evidence and fake dispatch establish
the routing intent; owner click acceptance remains the exact UI end-to-end gate.

Menu-only recovery fixture PASSed on the final bundle: 18s host pause preserved
healthy collector; frozen collector replaced once; fixture children cleaned up.
Signed local trial refreshed with previous bundle retained. Host88762/observer88765
confirmed running, no renderer. Sanitized live observation showed one working
coordinator and zero attention routes (no pending question/error at inspection).
CUA returned the known status-only AX timeout despite process launch success.
No actual attention record was fabricated in the bridge; no hooks, hardware,
startup, schedules, publication or commits were changed.

## Owner end-to-end acceptance

After the retention fix and branded-card refresh, the owner clicked Open chat
on the actual test-question card and explicitly confirmed: "Yes, this exact
session." This establishes real user-click navigation to the intended local
Codex conversation for this tested Mac/app revision. It does not extend exact
routing acceptance to remote hosts or other providers.
