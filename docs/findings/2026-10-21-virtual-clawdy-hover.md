# Menu-bar hover and attention expansion — 2026-10-21

Owner requested a Dynamic Island-like expansion on hover and automatic expansion
for question/error/red status, with a useful action to reach the source app.
Private native candidate; no website/public release or hardware changes.

## Design intent

A 332×164pt dark translucent panel anchors 6pt below the menu-bar button and
stays within its screen. Intentional hover entry (~120ms) and a short exit grace
(~280ms) allow the pointer to cross the gap into the interactive panel. Finite
~180ms expansion/fade respects Reduce Motion and Pause. No recurring animation
or cursor polling is required. Normal idle remains menu-bar-only.

Question/error opens once per attention episode without stealing focus.
Dismissal survives status revisions, provider churn and transient offline states;
a confirmed non-attention state or explicit mode change arms the next episode.
Close/outside-click dismiss passive panels. Explicit keyboard menu invocation
can focus controls and use Escape; no global keyboard/accessibility permission
is requested to intercept keys in another app.

## Action routing and privacy

The collector now emits optional enum-only attention_providers. B records supply
question targets, R records error targets. Working Y providers remain separate;
no unrelated busy provider becomes the target of an error/question action.
Absent legacy field means no action targets; malformed/null values are rejected.
No session IDs, prompts, arbitrary URLs or chat titles enter the snapshot.

A read-only local audit established installed Codex supports
codex://threads/<UUID>, but registry IDs alone cannot establish local/remote
routing or other providers' deep links. Exact-chat links are deferred rather
than sending the user to a guessed chat. Explicit app-level buttons use fixed
installed app identities, with honest Terminal fallback for CLI providers.
No provider app launches automatically or from a demo fixture.

## Review and checks

Static native preview/source review found no layout/contrast blockers. Review
caught hover-dismiss latching, action-button focus loss on WIP updates, and late
app-launch callbacks affecting newer alerts; these were corrected before trial.
Effective app destinations are deduplicated; Claude/Gemini share one Terminal
button. Native controls retain identity across count/provider/phrase churn.
Failure remains inline; stale callbacks cannot dismiss or overwrite new targets.

Root verification: 227 integrated Python tests PASS; native host self-test PASS
(including optional target decode/validation); offscreen attention self-test PASS;
real-window attention fixture PASS. The fixture uses the actual native panel
and production hover entry/exit handlers with fake app launching, not global
input synthesis. It covers dwell cancellation, crossing the gap, delayed exit,
auto episode/dismissal, reconnect suppression, fixed destinations, demo no-launch,
inline errors, delayed callbacks, stable buttons, keyboard cancel path, geometry,
Reduce Motion selection and cleanup. It does not constitute actual VoiceOver
speech, hand-operated pointer acceptance or exact-chat navigation acceptance.

## Recovery and trial refresh

The corrected menu-only recovery fixture PASSed again on this full candidate:
18-second host pause did not replace a healthy collector; an actually frozen
collector recovered exactly once; no renderer launched; all fixture children
were cleaned up. Code signature verification PASSed before refresh.

The private local trial was replaced with the tested bundle and relaunched:
host PID85877 and owned observer PID85878, with no floating renderer. The bundled
collector emitted one working coordinator record and empty attention targets.
The previous signed bundle and SHA256 metadata remain in the local cache.
CUA launch returned the known status-only AX timeout, while process inspection
confirmed the launch; hand-operated hover confirmation remains pending. No
hooks, startup, bridge, Bluetooth or USB device state was changed; the accepted
physical LED blink firmware was untouched. No commit/push/publication occurred.
