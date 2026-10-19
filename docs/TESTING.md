# Tester acceptance and evidence

Record OS/Python version, board manufacturer/revision, firmware commit/bootloader, exact BLE name, and date. Keep credentials, local user paths and private chat contents out of shared reports.

1. Factory check: soldered connections, resistor/LED orientation, green P0.10 / amber P1.11 / red P1.13. Confirm each LED visibly lights.
2. First customer install on a clean Mac user account: pre-flashed board powered externally, no USB data cable, `python3 install.py --ble-name <label>`. Approve Bluetooth and hooks; confirm it does not select the developer's board.
3. Run manage_hooks.py status and scripts/verify_hardware.py. Board reports BLE; red, amber, green, blink and off are observed; tracking resumes afterwards.
4. Real chat: prompt → amber, finish → green, supported input/approval request → blinking red. Explicit synthetic error → red. Confirm concurrent chats preserve the most urgent state.
5. Board power cycle: with USB removed and an approved battery/harness, switch off until all LEDs are dark; switch on. Wait for reconnect and check the latest host state. Repeat ten times and record each result/time. Do not call a software reset a battery test.
6. Maintenance reset: firmware accepts X on USB only. This restarts the MCU and tests advertising/reconnect; it does not prove battery/charger operation. GPIO/host state must resynchronize.
7. Restart the owned helper; verify it restores recent session state and reconnects. Then log out/in and reboot the Mac separately. Log-in startup and Bluetooth permission must persist; helper restart alone is not evidence of an OS reboot.
8. Disable/re-enable Mac Bluetooth and test sleep/wake. Commands issued while disconnected should be reflected after reconnection. Record delays and failures rather than promising instant recovery.
9. Battery/charging: verify charger compatibility first, then record current/temperature and runtime under the documented LED workload. Do not use prototype results as a production battery specification without repeat testing.
10. Removal: owned hooks/service removed, unrelated hooks/config intact, backups retained. Reinstall and rerun acceptance.

Hardware-free checks: `~/.local/share/trafficlights/venv/bin/python -m unittest discover -s tests -v` and `git diff --check`. These do not substitute for visual or power tests.

Current evidence: prototype visual colors confirmed by the user; real hooks and BLE GPIO signals verified; helper reconnect verified. Physical battery switching, runtime/charging, clean-customer onboarding and full Mac reboot remain separate acceptance tasks until recorded in CHANGELOG.md.

Provider acceptance: follow docs/PROVIDERS.md for two same-provider chats and mixed-provider chats, verifying real hook dispatch and physical state. Claude/Gemini/Cursor installer and payload tests do not replace this acceptance.

## PWM and Windows integration acceptance

Green Q reports should include green_pwm_duty=32768 and green_pwm_frequency=5000 with the default profile. Confirm the LED visually as well; boolean GPIO reports alone do not prove brightness. Test Y through a real Gemini tool turn and G only after AfterAgent, including two concurrent chats. Native Windows startup and real-provider acceptance remain required for this revision. Local automated tests include quoting, profile preservation, ambiguity refusal and PWM validation; Windows CI is hardware-free. See [2026-10-07 findings](windows/findings/2026-10-07-mac-integration.md).
# Customer enrollment candidate acceptance

The new enrollment code is hardware-free tested only. Before customer release:

1. Use the exact private candidate ZIP on a clean native Mac account. Power a
   factory-flashed toy externally, with no USB data path to the laptop.
2. Run `install.py --onboard`. Verify dependency/permission prompts, provider
   choice, physical identification and cancellation before mutation.
3. Repeat with two toys in the room and duplicate initial names. Confirm explicit
   selection and that only the intended unit changes. The normal bridge must
   refuse duplicate names rather than pick the first one.
4. Choose laptop + nickname; record the generated name and full device ID. Power
   the toy off/on and confirm persisted name, matching identity and reconnect.
5. Preserve the exact wiring/OLED profile through factory update and rename.
   Test old firmware `--keep-name`; unsupported rename must stop honestly.
6. Require BLE GPIO acknowledgements and visible LEDs, then real prompt/finish
   and supported attention/error signals from each selected provider.
7. Verify repeat install, disabled/malformed provider preferences, an interrupted
   install, old-host release, reassign, login/reboot and removal/reinstall.
8. Qualify ESP32-C3 separately with confirmed GPIO/polarity and compiled factory
   firmware. Host protocol recognition is not ESP32 electrical acceptance.

The wizard can require physical confirmation, but it cannot infer human visual
evidence from a GPIO response. Do not record skipped steps as passed.
