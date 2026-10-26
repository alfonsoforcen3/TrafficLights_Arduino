# Attention panel click window — 2026-10-21

Owner's actual test question showed the panel and then it disappeared almost
immediately, so exact-chat navigation was not yet accepted. The controller
immediately replaced attention content/targets and hid an auto-pinned panel on
any nonred report. Async test-question invocation followed by turn-ending status
can therefore remove the action before a person clicks. This is a UI retention
bug; traffic hooks remain observers and must not force model continuation.

The correction retains the recent alert and exact-chat action for a bounded
20-second minimum click window, with explicit recent/status-changed wording if
new reports have cleared the attention state. The menu bar continues to show
current status. Hover/key interaction can retain the card until exit/dismissal;
explicit close, menu, sleep, mode change and shutdown cancel retention. One
cancellable generation-checked deadline replaces recurring polling. Retention
must not renew on each one-second report or replay stale launch callbacks.

Native full-host and real-panel fixture PASS. Targeted cases verify B→G retains
the exact button while showing current0WIP, B→Y preserves the route with current
working providers/count, unknown/offline churn does not extend the20s deadline,
recent-route explicit fake dispatch works, inline failure keeps the recent note,
hover/key protection and leave expiry work, dismissal cancels old work, semantic
new route invalidates previous callbacks, and a real short async deadline expires
without status polling. Shutdown clears retained IDs/work. Existing Python code
was unchanged in this iteration (235-test baseline remains applicable).

Menu-only pause/stalled-collector recovery fixture PASSed on this candidate.
The signed retention build was installed and relaunched, host95742/collector95747
confirmed running. Previous bundle retained. Owner then requested product-photo
branding; the second actual Open chat test is pending while branding is prepared.
No pending question was fabricated in the bridge, and no hooks were altered.

Owner repeated the actual test after refresh and confirmed Open chat reached
this exact session. The prior disappearing-card failure no longer prevented
that click. This confirms practical clickability/navigation for this scenario;
it is not a measurement of every deadline or an extended UI stability test.
