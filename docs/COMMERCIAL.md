# Commercial distribution and source protection

## Chosen direction

The owner selected **private implementation, public setup/docs, and a signed Mac installer** on 2026-10-01.

- Keep implementation, firmware source, build tooling, development history and factory records in the private source repository.
- Publish customer setup, access explanations, compatibility, support, release notes and installer download/checksum instructions in a separate public repository with a fresh documentation-only history.
- Ship wired, pre-flashed, tested hardware. Give customers a signed/notarized standalone companion installer rather than a source checkout.
- Give selected developers/testers private-source access only when needed, under separately agreed terms.

The current py2app alias helper is a developer runtime, not that standalone installer. Packaging, signing credentials, notarization, updates, installer licensing and third-party notices still need implementation/review. Public setup must explicitly say when no consumer installer is available; never offer a fabricated download.

## What this protects

A private repository prevents ordinary anonymous source browsing and cloning. Signed binaries reduce casual source access and improve installation trust, but are not a guarantee against reverse engineering. Obfuscation adds maintenance and debugging cost; it should not be the main commercial protection for a small local indicator.

The CircuitPython prototype stores readable .py firmware on its filesystem. Copying it into a zip, hiding files, or suppressing a drive's normal appearance does not make the implementation confidential. Compiled firmware and deliberate hardware readout protection would be a separate engineering project with provisioning, recovery and servicing trade-offs.

Any implementation that must execute on a customer's computer or hardware can be inspected to some extent. Never embed API credentials, signing private keys or shared service secrets in the app or firmware. Optional future cloud services can keep their own implementation private, but ordinary light control should remain usable locally without sending prompt content to a server.

Existing public copies cannot be recalled by making the repository private. Do not rewrite or delete development history as a supposed secrecy measure. Preserve source history privately and start a separate clean public documentation history.

## Licensing and dependencies

No open-source license has been added. Commercial customer terms, tester permissions, documentation terms, contributor terms and third-party redistribution obligations need a deliberate owner decision before broad distribution. Do not add MIT/Apache terms just to make the repository appear complete. A private repository is an access control choice; a license is a permission/legal choice.

GitHub explains that without a license, default copyright applies; GitHub's public-repository terms still allow viewing/forking through the service. This does not prevent someone from independently building a similar idea. Obtain appropriate legal advice for enforceable commercial terms and relevant hardware/product obligations rather than relying on obfuscation.

Reference: [GitHub repository licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

## Release handoff

1. Pass the [release gates](RELEASE_READINESS.md).
2. Build a standalone companion with stable installed paths and a deliberate signing identity; remove dependence on this developer's checkout/venv.
3. Sign and notarize, verify on a clean Mac, and record package checksum/version.
4. Publish only approved binaries and reviewed customer documents to the public setup repository.
5. Verify a normal customer can install without private-source credentials and can uninstall cleanly.
6. Keep factory provisioning, recovery instructions and rollback artifacts available to authorized maintainers.
