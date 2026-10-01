# Commercial release readiness

**Current status: tester preview.** Documentation and automated checks improve maintainability; they do not establish production reliability or battery safety. Record acceptance evidence in CHANGELOG.md and the release report before closing a gate.

| Area | Established evidence | Gate still open |
| --- | --- | --- |
| Prototype LEDs and BLE | User confirmed visible colours; GPIO acknowledgements tested | Repeat across production board batch |
| Local Codex | Real prompt/stop dispatch and working indicator | Full clean-customer lifecycle acceptance |
| Mixed-provider tracking | Separate IDs and synthetic Claude events preserve live Codex work | Real Claude/Gemini/Cursor turns and combinations |
| Reconnection | Helper restart recovers state; BLE operations have timeouts | Ten battery cycles, measured recovery, Bluetooth toggle, sleep/wake and full Mac reboot |
| Battery | Label recorded; initial battery-powered operation confirmed | Exact board charger/current, pack charge rating/protection, thermal/charge/endurance measurements |
| Customer onboarding | Source installer and existing-Mac prototype tested | Clean Mac without development tools/private-source access |
| Mac package | Developer alias app with Bluetooth usage declaration | Standalone runtime, signing, notarization, trusted downloads and updates |
| Device enrollment | Exact BLE name saved | Robust factory identity, controlled enrollment, protection against nearby cross-control |
| Recovery/removal | Backup/merge/removal regression tests | Real removal/reinstall and factory recovery acceptance |
| Quality checks | Hardware-free regressions and documentation checker | Review hosted CI results; CI is not physical acceptance |
| Commercial distribution | Owner chose private source + public setup/docs | Approved terms/notices, final installer distribution and support process |

## Minimum release record

Record commit/version, board revision and batch, firmware/bootloader, battery/charger verification, package checksum/signature/notarization, macOS/application versions, all acceptance results, known issues and rollback instructions. Remove user paths, credentials and chat contents from shared evidence.

Do not change a label to “production” solely because the test suite passes. The release owner decides when the evidence is sufficient to ship, with appropriate product-safety/legal review.
