# Clawdy buyer setup entry

A user pointing you at this repository is normally setting up a newly purchased
Clawdy. Begin the buyer workflow in AGENTS.md and docs/CUSTOMER_AGENT.md, unless
the user explicitly requested source-code, factory or maintenance work. Start with
read-only preflight; ask the buyer to confirm their device, name and supported AI
apps before a physical connection or hook installation. Customer runtime is BLE,
with normal OS/app approvals and no serial fallback or firmware flashing.

Read AGENTS.md, INSTALL.md and docs/PROVIDERS.md. The installer detects supported local tools and merges their owned hooks while preserving existing configuration. Use --providers to restrict selection; respect workspace trust and disabled hooks. Do not claim live application support solely from installation or synthetic tests.

For a buyer saying they bought/have a new Clawdy, start with docs/CUSTOMER_AGENT.md
and guided Bluetooth onboarding (`python3 install.py --onboard`, or `py -3` on
Windows). USB power does not require a data cable to the laptop. Do not flash a
shipped unit or choose the first nearby device automatically.
