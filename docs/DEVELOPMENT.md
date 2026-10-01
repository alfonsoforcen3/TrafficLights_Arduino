# Development and release workflow

Keep reusable setup in the repository and machine-specific paths/names in local runtime configuration. Pin tested downloads/dependencies, validate checksums, and preserve backups. Do not commit credentials, user hook trust, TCC settings, device backup binaries, generated apps or logs.

For an iteration: describe the problem and final behavior; update the relevant guide and CHANGELOG.md; run unit checks plus the affected hardware acceptance; state remaining unverified behavior; stage explicit project paths; review staged diff; commit. Push only when publication is authorized. Do not auto-commit unrelated projects or future edits merely because a past iteration was committed.

The manufacturer should ship flashed/tested boards with a BLE-name label and firmware version. Customers install the Mac companion software and approve access locally. Keep source available to testers for inspection, updates and recovery. A blank-board/USB-flash route remains optional for DIY developers. Build a signed/notarized installer and proper device enrollment before replacing this tester workflow with consumer distribution.

Local developer firmware backups are intentionally private. The adjacent claude-mascot-3d directory is an independent Git checkout and must not be staged into this repository accidentally. Its assets/license and release process are separate.
