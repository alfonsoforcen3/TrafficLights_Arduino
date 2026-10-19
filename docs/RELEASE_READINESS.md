# Commercial release readiness

**Current status: tester preview.** Documentation and automated checks improve maintainability; they do not establish production reliability or battery safety. Record acceptance evidence in CHANGELOG.md and the release report before closing a gate.

## Private customer candidate — 18 October 2026

The owner requested preparation in private and will decide publication later.
`install.py --onboard` adds terminal BLE discovery, explicit/visual device
selection, capability-checked naming and selected-provider setup. A clean ZIP
with hashes can be built using `scripts/build_customer_bundle.py`. It contains
readable runtime code and no factory firmware; it is not a signed installer.
Do not upload it or change repository visibility without a release request.

The QR landing page is live at the existing URL; its public installer controls
remain previews. Customer access stays blocked until an approved package is
published. See [customer guide](CUSTOMER_SETUP.md), [agent import instructions](CUSTOMER_AGENT.md)
and [candidate findings](findings/2026-10-18-customer-onboarding.md).

Physical rename persistence, clean-Mac setup, Windows native acceptance,
production-unit wiring and real-provider dispatch are still release gates.
Battery gates apply only to battery-equipped units; a USB-powered batch still
needs power-source, wiring and device lifecycle acceptance.

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
