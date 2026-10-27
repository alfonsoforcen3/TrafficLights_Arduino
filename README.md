![Traffic Lights — your AI activity, at a glance](assets/banner.svg)

# Clawdy

A USB-powered Bluetooth desk companion for your local AI agents. See when work is running, when attention is needed, and when your tracked chats have finished—without watching every window.

**Native desktop tester preview** · Mac verified · Windows acceptance pending · Linux unsupported

nRF52840 hardware · OLED reactions · Working-session count · Local provider icons

[Buyer setup](docs/CUSTOMER_SETUP.md) · [Install and activate: Mac / Windows / Linux status](docs/INSTALL_ACTIVATE.md) · [Factory/maintainer installation](INSTALL.md) · [Provider integrations](docs/PROVIDERS.md) · [Documentation](docs/README.md) · [Release readiness](docs/RELEASE_READINESS.md)

## One light, all your tracked chats

| Signal | Meaning |
| :--- | :--- |
| 🟢 Green | All tracked chats are ready or finished |
| 🟡 Amber | At least one chat is working |
| 🔴 Blinking red | A supported input or permission request needs attention |
| 🔴 Solid red | An explicit error signal was received |

Each chat has a separate provider/session record. The shared light prioritizes **input → error → working → ready**. Finishing one chat leaves the light amber while another is working. Green settles for 1.5 seconds after completion; brief input signals are filtered for 0.8 seconds. [How multiple chats work →](docs/MULTIPLE_CHATS.md)

## Set up your Clawdy with your AI

Power your assembled Clawdy from USB and keep it near your laptop. Its searching
lights blink together. USB power can come from a wall supply; a USB data cable
to the laptop is not required for Bluetooth setup.

Tell your **local AI assistant with terminal access**:

> I bought a new Clawdy and it is powered on near this computer. Set it up for me using https://github.com/alfonsoforcen3/TrafficLights_Arduino. Read AGENTS.md and docs/CUSTOMER_AGENT.md, help me select and identify my toy, give it a nickname, configure my installed supported AI apps, and verify the lights. Guide me through normal Bluetooth and app approvals.

Once the assistant has this repository, “I have a new Clawdy connected to this
machine; set it up” is enough to start the same guided workflow. Ordinary browser
chat cannot run local commands or configure Bluetooth by itself.

The assistant clones this public source into a stable local folder, checks the
platform and prerequisites, then runs the terminal wizard:

```bash
python3 install.py --onboard
```

On native Windows, use `py -3 install.py --onboard`. macOS has physical prototype
evidence; native Windows customer acceptance is still pending. Linux/WSL is
unsupported. The AI must let you select and visibly identify the correct toy,
review provider hook permissions, and confirm the LEDs. It must report unfinished
checks instead of calling an installation verified just because a process runs.

New factory firmware supports a name derived from your laptop, chosen nickname
and unique unit suffix. Older shipped firmware can keep its current name; normal
setup does not reflash a toy. Only installed hook-capable applications are
configured; setup does not download AI apps or require a bridge API key.

[Step-by-step customer setup](docs/CUSTOMER_SETUP.md) ·
[Instructions for your AI](docs/CUSTOMER_AGENT.md) ·
[Provider capabilities](docs/PROVIDERS.md)

A source bundle can also be prepared using
`python3 scripts/build_customer_bundle.py`. Signed consumer packaging and
clean-customer acceptance remain release work.

### Private virtual companion prototype

The [native macOS prototype](desktop/macos/README.md) displays traffic lights,
reported WIP and AI apps in the menu bar. It observes an already-running local
companion without starting hardware or installing hooks. Demo data and the
floating island are explicit options. This is a private development build, not a
customer-ready app. See the [design and acceptance plan](docs/VIRTUAL_CLAWDY_PLAN.md).

### Existing maintainer/tester installation

This repository is public. The guided onboarding above is the buyer entry point; the exact-label commands below are for existing units and maintainer diagnostics. A standalone signed consumer installer is still pending.

Boards should ship wired, flashed, tested, and labelled with their Bluetooth name. Testers install the native Mac or Windows companion and approve local access; routine operation needs no USB data connection.

```bash
git clone https://github.com/alfonsoforcen3/TrafficLights_Arduino.git
cd TrafficLights_Arduino
python3 install.py --ble-name TrafficLight-ABCD
```

Replace `TrafficLight-ABCD` with **your unit's label**. The installer creates an isolated Python environment, installs the Bluetooth login helper, detects supported local AI tools, and preserves unrelated hooks/settings. Approve Bluetooth access for **Traffic Light Bridge** and review each provider's hooks/workspace trust. Then check:

```bash
python3 manage_hooks.py status
```

For unflashed units, USB name discovery, prerequisites and recovery, use the [full installation guide](INSTALL.md).

## Local integrations

| Application | Adapter | Verification |
| :--- | :--- | :--- |
| Codex / locally orchestrated Work | Prompt, tools, input, completion, explicit errors | Real hooks and prototype BLE verified |
| Claude Code | Prompt, tools, permission/questions, completion, failed turns | Installed here; payload/mixed-session tests pass; live turn acceptance pending |
| Gemini CLI | Agent/model/tools, permission notifications, completion | Installer and payload tests pass; live CLI acceptance pending |
| Cursor Agent | Prompt, thought/response, completion/errors | Installer and payload tests pass; live app acceptance pending; no permission-wait signal |

This integrates with **applications**, regardless of their underlying model. Ordinary AI websites and cloud agent VMs do not automatically reach this local bridge. [Adapter capabilities, access review, and custom integrations →](docs/PROVIDERS.md)

## Useful commands

```bash
python3 scripts/provider_setup.py --detect               # Preview detected applications
python3 install.py --providers codex claude               # Restrict hook installation
python3 install.py --no-hooks                             # Update the helper, preserve hooks
python3 manage_hooks.py status                            # Sessions, connection and GPIO report
python3 manage_hooks.py disable                           # Remove owned hooks and login service
```

The explicit hardware colour test is `python3 scripts/verify_hardware.py`. It deliberately cycles the LEDs; run it during setup or diagnostics, not during ordinary conversations. Removal retains recovery backups, runtime packages and flashed firmware. [Troubleshooting →](docs/TROUBLESHOOTING.md)

## Inside the repository

| Path | Purpose |
| :--- | :--- |
| `install.py` / `manage_hooks.py` | Setup and operator commands |
| `scripts/` | Provider adapters, local bridge, Bluetooth helper and provisioning |
| `firmware/nicenano/` | Tested nRF52840/CircuitPython board profile |
| `firmware/traffic_light/` | Legacy Arduino wired profile |
| `docs/` | Customer, factory, tester and developer guides |
| `tests/` | Hardware-free regression coverage |

[Contributing](CONTRIBUTING.md) · [Security and privacy](SECURITY.md) · [Changelog](CHANGELOG.md) · [Commercial distribution and source policy](docs/COMMERCIAL.md)

## Before commercial release

This is a working **tester preview**, not a completed consumer release. Clean-customer onboarding, USB power-cycle recovery, full laptop reboot, live additional-provider acceptance, signed packaging and device enrollment remain release gates. [Track the evidence and remaining work →](docs/RELEASE_READINESS.md)

The verified prototype uses a nice!nano-compatible clone with **P0.10 green,
P1.11 amber, P1.13 red**; individual units can have different recorded profiles.
Use the supplied USB power connection and confirm the exact board before factory
work. [Hardware](docs/HARDWARE.md).

Source is publicly readable. Public visibility does not grant an open-source
license or establish customer qualification; no open-source license is supplied.
Dependencies retain their own terms. See [commercial policy](docs/COMMERCIAL.md).

The local [Clawdy dashboard](web/index.html) shows current connection and light
status. It reads only the local companion; the static website does not connect
to your laptop or simulate a live device.
