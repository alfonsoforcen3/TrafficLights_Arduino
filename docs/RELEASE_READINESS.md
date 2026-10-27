# Commercial release readiness

**Current status: tester preview.** Documentation and automated checks improve maintainability; they do not establish production reliability or USB power-input safety. Record acceptance evidence in CHANGELOG.md and the release report before closing a gate.

## Source onboarding candidate — 18 October 2026

The owner requested source-based customer onboarding. On 27 October 2026 the
owner made the repository publicly accessible; this source visibility does not
mean a signed installer or packaged customer release exists.
`install.py --onboard` adds terminal BLE discovery, explicit/visual device
selection, capability-checked naming and selected-provider setup. A local ZIP
with hashes can be built using `scripts/build_customer_bundle.py`. It contains
readable runtime code and no factory firmware; it is not a signed installer and
is not published automatically. The customer download/package release is still
a separate gate.

The QR landing page remains at its existing URL; public installer controls are
still previews. Buyers can use the source workflow in [customer guide](CUSTOMER_SETUP.md)
with a [terminal-capable local AI assistant](CUSTOMER_AGENT.md). See the
[candidate findings](findings/2026-10-18-customer-onboarding.md).

Clean-Mac setup, native Windows acceptance, production-batch wiring,
physical power cycles and real-provider dispatch remain release gates. One ESP32-C3
unit has factory USB firmware/identity/LED diagnostics and software-reboot name
persistence evidence, recorded separately from customer BLE enrollment.
Qualify the USB source, cable/connector, board wiring and reconnect lifecycle.

| Area | Established evidence | Gate still open |
| --- | --- | --- |
| Prototype LEDs and BLE | User confirmed visible colours; GPIO acknowledgements tested | Repeat across production board batch |
| ESP32-C3, unit 5D1C | Arduino-ESP32 3.3.2 / ArduinoJson 7.4.3 target build, backed-up USB upload with four verified region hashes, identity/GPIO diagnostics, complete rename acknowledgements and persistence across two software reboots; owner confirmed production search blink | Independent radio/BLE identity and GPIO delivery, physical power cycles, buyer-host approved real-provider turns and laptop-restart acceptance |
| Local Codex | Real prompt/stop dispatch and working indicator | Full clean-customer lifecycle acceptance |
| Mixed-provider tracking | Separate IDs and synthetic Claude events preserve live Codex work | Real Claude/Gemini/Cursor turns and combinations |
| USB power and reconnection | Helper restart recovers state; BLE operations have timeouts | USB input/cable qualification, repeated USB power cycles, measured recovery, Bluetooth toggle, sleep/wake and full Mac reboot |
| Customer onboarding | Source wizard contract includes read-only preflight, explicit BLE advertisement selection, nickname/provider consent and human verification gates | Clean buyer Mac onboarding, actual BLE firmware identity and GPIO handshakes, approved real-provider turns, and native Windows acceptance |
| Mac package | Developer alias app with Bluetooth usage declaration | Standalone runtime, signing, notarization, trusted downloads and updates |
| Device enrollment | Exact BLE name saved | Robust factory identity, controlled enrollment, protection against nearby cross-control |
| Recovery/removal | Backup/merge/removal regression tests | Real removal/reinstall and factory recovery acceptance |
| Quality checks | Hardware-free regressions and documentation checker | Review hosted CI results; CI is not physical acceptance |
| Commercial distribution | Public source repository; no signed customer package | Approved terms/notices, final installer distribution and support process |

## Minimum release record

Record commit/version, board revision and batch, firmware/bootloader, USB source/cable verification, package checksum/signature/notarization, macOS/application versions, all acceptance results, known issues and rollback instructions. Remove user paths, credentials and chat contents from shared evidence.

Do not change a label to “production” solely because the test suite passes. The release owner decides when the evidence is sufficient to ship, with appropriate product-safety/legal review.
