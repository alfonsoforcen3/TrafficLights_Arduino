# Development and contributions

Read AGENTS.md and docs/DEVELOPMENT.md. This is the private implementation repository for a commercial product; contributor and distribution terms must be agreed with the owner before external contributions or redistribution. No open-source license is implied.

## Local checks

Use an isolated environment; do not run installation or alter machine hooks just to edit documentation.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pyserial==3.5 bleak==0.22.3
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_docs.py
git diff --check
```

The GitHub workflow runs hardware-free tests only. It never flashes a board, contacts model APIs, installs user hooks or accesses Bluetooth. Linux test jobs do not establish Linux installer support.

## Changes

Keep installation commands stable so customers and approved hook definitions keep working. Update the affected guide and CHANGELOG.md. Include meaningful regression coverage for state/session/configuration changes; document-only edits need link/layout checks. Run physical acceptance only when the change requires it, and announce any intentional colour cycling.

Provider adapters must preserve unrelated configuration, use stable provider/session IDs, respect disabled hooks and policy, avoid returning approvals/continuation prompts, and include safe removal. Refer to docs/PROVIDERS.md for observed signal limitations.

Record actual test evidence and remaining limitations. Never claim live application acceptance from synthetic payloads alone. Commit explicit project paths; exclude logs, backups, device identifiers tied to users, credentials, generated bundles and independent checkouts.

## Pull requests

Explain the concrete problem, final behaviour and relevant validation. Use the template and identify affected hardware/application versions. Commercial release changes must satisfy docs/RELEASE_READINESS.md, not just pass unit tests.
