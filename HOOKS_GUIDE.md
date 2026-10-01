# Hooks, access, and removal

The installer merges owned command handlers into **~/.codex/hooks.json**. Each installed command uses the local Python environment and the absolute local scripts/traffic.py path. Entries carry `statusMessage: "Traffic light: …"` so updates/removal preserve unrelated hooks. Existing configuration is backed up in .backups/.

| Codex event | Signal |
| --- | --- |
| SessionStart | G |
| UserPromptSubmit | Y |
| PreToolUse / PostToolUse | Y |
| PermissionRequest | B |
| Stop / Interrupt | G |
| SessionEnd | remove that session |

Supported request_user_input tools are recognized by tool_name and emit B. A later work event emits Y again. Red comes from an explicit error payload or `R` command; not every unsuccessful tool result is an error. These hooks observe activity; they do not block tool execution or add model continuation prompts. They return `{}` on stdout.

Commands send session_id and state to 127.0.0.1:8765. The bridge combines chats and forwards the aggregate by BLE or USB. An acknowledgement that TCP accepted a command is distinct from a board GPIO acknowledgement. When no sessions remain, the bridge uses green standby. There is no unsupported `Notification` hook registered.

## User review

Codex requires trust of non-managed hook definitions. Review `/hooks` in the Codex CLI; changed paths/definitions can require new approval. The agent must not bypass this review. Local Codex / locally orchestrated Work are supported; ordinary ChatGPT chat and cloud-orchestrated Work do not use these local command hooks. See [official hooks documentation](https://learn.chatgpt.com/docs/hooks).

Bluetooth permission belongs to the Mac helper and is separate from hook trust. See [installation](INSTALL.md) and [Bleak's macOS permissions](https://bleak.readthedocs.io/en/latest/backends/macos.html).

## Disable

```bash
python3 manage_hooks.py disable
```

This removes owned Codex entries and unloads/removes the owned LaunchAgent. It also removes the old project's Gemini traffic-light entry if present; unrelated entries are preserved. Backups, the Python environment, built app and flashed board firmware remain for recovery. Disabling hooks is not a secure erase/uninstall of every file, nor a guaranteed physical power-off; use the battery switch and disconnect USB to power off.

Gemini and Claude examples in old revisions are legacy integrations, not currently verified installers. Agent instruction files for those tools point to the same supported installation workflow; that does not imply automatic hook integration with those agents.
