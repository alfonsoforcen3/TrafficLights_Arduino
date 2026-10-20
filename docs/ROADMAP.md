# Integration and product roadmap

Prioritize integrations by tester demand and lifecycle reliability. Add a provider only when stable chat IDs, start/completion semantics, permissions, error states and removal can be documented and tested. The bridge already accepts custom provider/session signals; existing hardware does not need a model-specific firmware change.

| Candidate | Why consider it | Next investigation |
| --- | --- | --- |
| OpenCode | Its plugin API documents session status/idle/error and permission events | Map payload IDs, retries, session deletion and background jobs; use a plugin rather than guessed settings hooks |
| Windsurf/Cascade | Its hooks document prompt and cascade-response activity | Verify current product/version, hook path/schema, completion timing, permission coverage and session identity |
| Copilot / VS Code agent tooling | Likely valuable where testers already work | Investigate the exact client/runtime and official extension/event interface; do not infer support from a model name |
| Custom local API wrappers | Existing provider/session signal interface | Document wrapper start/stop/error/input calls and ensure final cleanup on exceptions |
| Ordinary web AI chats | Useful audience, but no universal local lifecycle interface | Separate opt-in browser integration with explicit site permissions and privacy review; tab presence is not work detection |

OpenCode and Windsurf are **candidates, not installed or supported adapters in this release**. Do not auto-create configuration for them until an adapter is implemented and accepted.

Product work should come first: reliable battery/reconnect acceptance, clean-Mac onboarding, standalone signed/notarized installation, robust device identity/enrollment, and update/rollback. Expanding an unverified provider list does not replace those release gates.

The [Virtual Clawdy plan](VIRTUAL_CLAWDY_PLAN.md) proposes a macOS desktop
companion using the same status semantics, with an explicit virtual-only mode,
isolated rendering, bounded recovery and measurable private acceptance gates.
It is planning only; no virtual desktop app or compatibility claim is shipped.

References: [OpenCode plugins/events](https://opencode.ai/docs/plugins/), [Windsurf/Cascade hooks](https://docs.windsurf.com/windsurf/cascade/hooks). The latter documentation may redirect as product branding changes; verify the shipped client version before integration.
