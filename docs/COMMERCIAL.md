# Commercial distribution and source policy

## Current owner decision — 27 October 2026

The owner has made the TrafficLights_Arduino repository public and verified
anonymous access. This supersedes the 2026-10-01 decision to keep implementation
source private. Do not restore the older private-repository policy without a new
owner decision.

Public source visibility does not mean the project is licensed as open source,
qualified for customer use, or packaged as a consumer product. There is no
signed standalone installer or released prebuilt customer archive. Local build
outputs and candidate bundles are not published automatically. Keep signing
keys, customer configuration/logs, and factory-unit records private.

## What public source access means

Anyone may read the hosted source. A public repository alone does not grant a
license beyond the platform's applicable terms. No project open-source license
has been added. Obtain an explicit owner/legal decision before adding a license,
commercial customer terms, contributor terms, or redistribution commitments.

The repository still contains prototype and development material. Public access
does not establish that a build is safe, tested on every platform, supported by
an installer, or ready to ship. The USB-powered Clawdy communicates with its
local host over BLE; ordinary setup requires a terminal-capable local assistant
and the buyer's confirmation of device selection, OS permissions, provider trust,
and visible LEDs. Ordinary browser AI conversations cannot access local
Bluetooth or configure the host.

## Product and release boundary

Ship a USB-powered, pre-flashed, assembled, and tested product. Qualify its USB
power input, cable/connector, board revision, firmware, and reconnection behavior
before commercial release.

The current Mac helper is a locally built developer runtime, not a signed
standalone installer. Packaging, signing, notarization, updates, installer
licensing, and third-party notices still need implementation/review. Public
setup must identify the exact source-based workflow and its limitations; do not
offer a fabricated download or imply a signed customer package exists.

## Source protection

The repository is intentionally public by the owner's current decision. Remove
any old claim that repository privacy prevents source access. Signed binaries
may improve installation trust but do not guarantee against reverse engineering.
Obfuscation adds maintenance and debugging cost and is not a substitute for a
commercial model.

Any implementation that executes on a customer's computer or hardware can be
inspected to some extent. Never embed API credentials, signing private keys, or
shared service secrets in the app or firmware. Optional future cloud services
can keep their own implementation private, while ordinary local light control
should remain usable without sending prompt content to a server.

## Licensing and third-party material

GitHub explains that without a license, default copyright applies; its public
repository terms still allow viewing and forking through the service. This does
not prevent someone from independently building a similar idea. Obtain legal
advice for enforceable commercial terms and applicable hardware/product
obligations instead of relying on obscurity.

Reference: [GitHub repository licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

## Release handoff

1. Pass the [release gates](RELEASE_READINESS.md).
2. Build a standalone companion with stable installed paths and a deliberate
   signing identity; remove dependence on a developer checkout/virtualenv.
3. Sign and notarize, verify on a clean Mac, and record package checksum/version.
4. Publish only owner-approved binaries and reviewed customer documents.
5. Verify a normal customer can install without private-source credentials and
   can uninstall cleanly.
6. Keep factory provisioning, recovery instructions, and rollback artifacts
   available to authorized maintainers.
