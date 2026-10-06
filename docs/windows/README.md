> Native macOS/Windows auto-selection is now implemented. See [Windows installation](INSTALL.md) for current commands, reported evidence and pending native acceptance checks. Older macOS-only or Windows-pending statements below describe the earlier release.

# Windows companion work

**Windows support has not yet been implemented or physically verified.** The current installer is macOS-only. These documents hand implementation and evidence capture to the agent on the Windows laptop.

1. Clone the private repository with an authorized GitHub account.
2. Give the Windows agent the complete [implementation prompt](AGENT_PROMPT.md).
3. Have it inspect the actual laptop, implement native Windows support, install and verify it, then record results using the [findings template](FINDINGS_TEMPLATE.md).
4. Keep redacted run reports in `docs/windows/findings/` and raw/private evidence in ignored `.backups/windows/`.

First Clawdy is already flashed and named `first clawdy`. Its green GPIO is P0.09, amber P1.11, red P1.13. Do not reflash it for laptop migration. The previous Mac's bridge/hooks were disabled on 2026-10-06; verify that no other host has reclaimed it. Read [handoff instructions](../LAPTOP_HANDOFF.md).

Suggested message to the Windows agent:

> Read AGENTS.md, docs/windows/README.md and the complete docs/windows/AGENT_PROMPT.md. Execute the Windows implementation/install/verification assignment, log redacted findings with docs/windows/FINDINGS_TEMPLATE.md, and commit/push the related work. First Clawdy is already flashed; do not overwrite its firmware/profile for installation. Clearly distinguish implemented, tested, blocked and not-run results.

A prompt being committed is not proof of a functioning Windows installer. Update support claims only after real Windows BLE acknowledgements and provider acceptance have been recorded.
