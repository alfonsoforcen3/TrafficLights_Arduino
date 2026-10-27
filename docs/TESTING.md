# Tester acceptance and evidence

Record OS/Python version, board manufacturer/revision, firmware commit/bootloader,
exact BLE name, USB power source/cable, and date. Keep credentials, local user
paths, and private chat contents out of shared reports.

1. **Factory check:** verify soldered connections, resistor/LED orientation,
   common ground, and the documented GPIO profile. Confirm each LED visibly
   lights. Software reports cannot detect a poor physical connection.
2. **Customer onboarding:** use the USB power connection for the pre-flashed
   toy; normal computer communication is BLE and needs no USB data connection.
   Run `python3 install.py --onboard` on native macOS. Ask the buyer to select
   the exact toy and chosen providers; never select the first scan result.
   Clean-customer acceptance is still pending. Native Windows syntax is
   `py -3 install.py --onboard`, but Windows onboarding acceptance is pending.
3. **Status and LEDs:** run `manage_hooks.py status` and
   `scripts/verify_hardware.py --transport ble`. Require BLE transport and current
   GPIO acknowledgements; observe red, amber, green, blink, and off. Confirm
   tracking resumes after the verification sequence.
4. **Real chats:** prompt → amber, finish → green, supported input/approval
   request → blinking red, and explicit synthetic error → red. Confirm concurrent
   chats preserve the highest-priority state. A synthetic signal is not a real
   provider test.
5. **USB power cycle:** disconnect the toy's USB power until its LEDs go dark,
   reconnect USB power, and wait for BLE advertising/reconnection. Verify the
   current host state returns. Repeat ten times if practical and record every
   result and recovery time. This tests the USB-powered product's power/reconnect
   path; it does not replace a software reset test.
6. **Maintenance reset:** firmware accepts X over USB data only. This restarts
   the MCU and tests advertising/reconnect; it is not a power-off test. GPIO and
   host state must resynchronize.
7. **Host lifecycle:** restart the owned helper; verify it restores recent session
   state and reconnects. Test logout/login and OS reboot separately. Disable and
   re-enable Bluetooth and test sleep/wake. Record delays and failures rather
   than promising instant recovery.
8. **Removal:** confirm owned hooks/service are removed, unrelated hooks/config
   remain intact, and backups are retained. Reinstall and rerun acceptance.

Hardware-free checks use the installed environment:

```bash
~/.local/share/trafficlights/venv/bin/python -m unittest discover -s tests -v
git diff --check
```

On native Windows, use the documented `venv\\Scripts\\python.exe` path. These
checks do not replace visible LED, USB power, BLE, or provider acceptance.

Current evidence includes owner-confirmed prototype LED colors, real hook and BLE
GPIO signals, and helper reconnect. Clean-customer onboarding, USB-power cycles,
full Mac reboot, and native Windows onboarding remain separate acceptance tasks
until recorded in CHANGELOG.md.

Provider acceptance: follow [PROVIDERS.md](PROVIDERS.md) for two same-provider
chats and mixed-provider chats, verifying real hook dispatch and physical state.
Claude/Gemini/Cursor installer and payload tests do not replace this acceptance.

## PWM and Windows integration acceptance

Green Q reports should include `green_pwm_duty=32768` and
`green_pwm_frequency=5000` with the default profile. Confirm the LED visually as
well; boolean GPIO reports alone do not prove brightness. Test Y through a real
Gemini tool turn and G only after AfterAgent, including two concurrent chats.
Native Windows startup and real-provider acceptance remain required for this
revision. Local automated tests include quoting, profile preservation, ambiguity
refusal, and PWM validation; Windows CI is hardware-free. See the
[2026-10-07 findings](windows/findings/2026-10-07-mac-integration.md).
