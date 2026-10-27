# Security and privacy

This system is a local activity indicator. It should never store or forward prompts, transcripts, account credentials or provider API keys. Hooks pass a provider/session ID and state to the local bridge; Bluetooth carries colour commands and GPIO reports.

## Current boundaries

- The bridge listens on 127.0.0.1:8765 and is unauthenticated. Do not expose it through network forwarding or bind it to external interfaces.
- The prototype BLE service has no encrypted bonding/enrollment workflow. Nearby control and device-name collisions remain commercial-release concerns.
- Hook commands execute with the local user's privileges. Keep the checkout/runtime in trusted locations; preserve provider trust, disabled-hook preferences and managed policy.
- Do not patch macOS privacy databases, fabricate hook trust, disable Gatekeeper, or request passwords in chat. Approvals belong in normal app/OS dialogs.
- The developer alias bundle and unsigned source installation are not a production package. Keep signing keys/credentials outside source, app bundles, firmware and logs.

## Reporting

For ordinary setup failures, use the troubleshooting guide and bug-report template. Include versions and sanitized state evidence; never attach provider settings, full hook payloads, private chats, keys or firmware backups blindly.

For a vulnerability involving credentials, execution, enrollment or privacy, contact the repository owner through an established private channel. If GitHub offers private vulnerability reporting for this repository, use that flow; its enablement is not assumed. Do not put exploit details or secrets in a public issue.

This preview has no published commercial security-support period. Release support and update policy must be defined before consumer distribution.
