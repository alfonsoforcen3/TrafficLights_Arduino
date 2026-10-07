# Provider adapters and automatic discovery

The shared bridge tracks `provider:session_id` records. Two Codex sessions, two Claude Code sessions, or Codex + Claude + Gemini + Cursor can coexist. The highest-priority state wins: input → explicit error → working → ready. A provider finishing removes no other provider's work. See [multiple chats](MULTIPLE_CHATS.md).

## Install detected tools

```bash
python3 scripts/provider_setup.py --detect  # read-only inventory
python3 install.py                         # install bridge + hooks for detected supported tools
python3 install.py --providers codex claude gemini cursor  # explicit selection
python3 install.py --providers claude       # only selected hooks; other hooks remain
python3 install.py --no-hooks               # update shared bridge only
```

Detection checks known executable names, known app bundles in /Applications or ~/Applications, and actual user configuration files. Empty folders and the old ~/.gemini/config/hooks.json file are not Gemini CLI installation evidence. Detection can find stale settings or an app with no usable local agent mode; it is an inventory, not a version/authentication/runtime guarantee. Nonstandard executable locations can be selected explicitly. The installer does not install AI providers, sign into them, buy credits, or start paid model runs.

Installation backs up configuration in .backups/, adds only owned entries, and preserves unrelated hooks/settings. Repeating setup does not duplicate owned hooks. Unselected providers remain configured; selection is not removal. Malformed configuration or an explicitly disabled hook system is left unchanged and reported as an error. Resolve that error and rerun; earlier providers may already have been installed. Provider workspace trust, managed policy and project-level overrides still apply. Never override those restrictions automatically.

## Integration matrix

| Provider/application | User configuration | Signals | Evidence |
| --- | --- | --- | --- |
| Local Codex / locally orchestrated Work | ~/.codex/hooks.json | prompt/tools Y; permission/input B; stop G; explicit error R; session end removes | Real local hooks/BLE verified |
| Local Claude Code | ~/.claude/settings.json | prompt/tools Y; permission/AskUserQuestion B; Stop G; StopFailure R; session end removes | Installer and payload tests; installed here; real Claude turn acceptance pending |
| Gemini CLI | ~/.gemini/settings.json | BeforeAgent/BeforeModel/tools Y; AfterAgent G; ToolPermission notification B; explicit error R; session end removes | Installer/payload tests; real CLI acceptance pending |
| Cursor local Agent | ~/.cursor/hooks.json | beforeSubmitPrompt/thought/response Y; stop G or R for status=error; session end removes | Installer/payload tests; real app acceptance pending; no pending-permission signal |

Claude hooks use seconds for timeout; Gemini uses milliseconds. Claude receives no stdout context from this observer. Gemini receives `{}` JSON. Cursor receives `{"continue":true}` only for prompt submission and `{}` for observation events. Cursor tool/permission-gating hooks are deliberately not registered. None of these adapters returns a tool approval, blocks a turn, modifies prompts, or requests continuation. Other policy hooks continue to make their own decisions.

Claude PostToolUseFailure returns working, because a failed tool can be retried while the agent continues. StopFailure reports an API-failed turn. Gemini only turns a ToolPermission notification into blinking red; unrelated notifications do not mutate the session. Cursor uses conversation_id, not generation_id, so successive turns belong to one record. Parent turns are tracked; independent background/subagent jobs are not exhaustively accounted for by these adapters.

The bridge's settling rules remain: immediate amber/error, 0.8-second input settling, 1.5-second green completion settling. Existing bare session IDs from earlier releases migrate to codex: IDs at helper restart. Firmware needs no provider-specific update.

## Review and removal

- Codex: review/trust `/hooks` entries as required.
- Claude Code: inspect `/hooks`, accept normal workspace trust, restart an existing session if needed. Disabled hooks/policy must be resolved by the user.
- Gemini CLI: inspect `/hooks panel`; check hooksConfig.enabled and disabled hook names; restart when settings require it.
- Cursor: inspect hooks configuration/output; user hooks are local. Verify lifecycle dispatch in a real Agent conversation.

```bash
python3 scripts/provider_setup.py --providers claude --disable
python3 scripts/provider_setup.py --providers gemini cursor --disable
python3 manage_hooks.py disable  # remove all owned adapters and stop shared login service
```

Provider-only removal leaves the shared bridge running; that provider's existing session records can linger until their expiry. Reset clears *all* sessions and should not be used during other active chats. Backups/runtime and board firmware remain intentionally.

## Other providers

This is application integration, not model detection. Cursor using an Anthropic, OpenAI, or Google model is still the Cursor adapter. Ordinary ChatGPT/Claude/Gemini websites, cloud agent VMs, Copilot, Windsurf, OpenCode, and other applications are not automatically configured by this release. Add an adapter only after checking its documented stable lifecycle/session interface. A browser tab being open does not prove the model is working.

A custom application or model-API wrapper can signal the same bridge explicitly:

```bash
~/.local/share/trafficlights/venv/bin/python scripts/traffic.py Y --provider custom --session-id chat-123 --silent
# When fully finished: G; waiting for input: B; explicit error: R; session closed: O.
```

Use a stable unique chat ID and lowercase provider namespace. Send both start and completion/close events; missing events leave stale records. Only state and IDs reach the local bridge, and only colour/GPIO data reaches BLE. Raw hook prompts/transcripts are not logged or forwarded. The localhost bridge is unauthenticated and intended only for local indicator control; do not expose port 8765 to the network.

## Acceptance tests

Run hardware-free tests, then start real conversations in each selected application. Submit work to A and B; finish A and ensure amber remains for B; finish B and ensure green settles. Repeat with provider mixes and input/error signals supported by each adapter. Confirm dispatch from the application as well as GPIO acknowledgements. Installation or synthetic payload tests alone do not establish live application support.

References: [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Gemini CLI hooks reference](https://geminicli.com/docs/hooks/reference/), [Cursor hooks](https://cursor.com/docs/hooks), [Codex hooks](https://learn.chatgpt.com/docs/hooks).

## Windows shell and turn tracking update (2026-10-07)

Gemini on native Windows uses PowerShell call-operator commands with literal quoted paths. POSIX/cmd.exe quoting is not interchangeable. The configured turn stays Y through BeforeAgent, BeforeTool and AfterTool and becomes G at AfterAgent; BeforeModel is omitted. Ownership cleanup preserves unrelated handlers. Mac tests and synthetic concurrent-session tracking passed; native Windows real-provider acceptance for this revision remains pending. Read [integration findings](windows/findings/2026-10-07-mac-integration.md) before promoting coverage.
