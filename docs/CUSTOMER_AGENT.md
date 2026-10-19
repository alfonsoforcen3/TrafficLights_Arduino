# Clawdy customer setup agent

This is a private review candidate. Follow README.md. Do not claim a signed
consumer release, native Windows acceptance, or ESP32 hardware acceptance.

When the owner says their pre-flashed Clawdy is powered and blinking:

1. Use native macOS or Windows Python 3.9+; Linux/WSL is unsupported.
2. Keep this extracted folder at a stable local path. Read the setup guide.
3. Preview with `python3 install.py --onboard --dry-run --ble-name LABEL --keep-name`.
   On Windows use `py -3` instead of `python3` where appropriate.
4. Run `python3 install.py --onboard` interactively in the user's terminal.
   Let the owner select the toy and choose their nickname; never select a nearby
   device on their behalf merely because it is first in a scan. An agent using
   noninteractive execution must first obtain the user's exact selected device,
   nickname/provider choices and then use the documented explicit arguments.
5. Respect OS Bluetooth permission and provider hook/workspace trust. Never
   bypass privacy databases, trust stores, managed policies or disabled hooks.
6. Require BLE firmware acknowledgements and the human's visible LED check.
   Run a real turn in each chosen local provider; synthetic tests are separate.
7. Do not flash a shipped unit during ordinary onboarding. Old firmware can keep
   its existing name; persistent wireless naming needs factory-updated firmware.
8. One laptop owns the connection at a time. Release the old laptop with
   `python3 manage_hooks.py disable` before moving the toy. Never reconnect a
   released laptop during code-only tests.

Do not install AI apps, purchase anything, request passwords in chat, publish
the bundle, or commit customer logs/configuration. No prompts are sent to BLE.
