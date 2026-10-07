# Windows companion setup and evidence

The shared installer now selects native Windows or macOS. Read [INSTALL.md](INSTALL.md) for Windows commands, dependencies, startup, updates and release. First Clawdy is pre-flashed: installing on Windows does not require USB storage writes.

The owner reports previous native Windows BLE/provider success and corporate USB write/network push restrictions. This revision was integrated on an authorized Mac; [2026-10-07 findings](findings/2026-10-07-mac-integration.md) distinguish hardware tests from remaining Windows acceptance.

Give the Windows agent the current [acceptance prompt](AGENT_PROMPT.md). Record sanitized outcomes using [FINDINGS_TEMPLATE.md](FINDINGS_TEMPLATE.md). Do not disable DLP, antivirus, firewall or trust controls. If corporate policy blocks installation or startup, record the exact redacted symptom and request the employer's normal IT approval. Use an authorized machine to update firmware or push source changes.

Only one laptop should control First Clawdy at a time. Follow [laptop handoff](../LAPTOP_HANDOFF.md), release the old companion, then install using its exact name `first clawdy`. No firmware or profile replacement is needed for a handoff.
