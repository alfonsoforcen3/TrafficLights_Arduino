# Older screen unit stale WIP — 26 October 2026

Owner reconnected the older screen-equipped unit and reported amber / 1 WIP while
idle. USB identified nice!nano UID suffix16DE, and the existing BLE bridge's
TrafficLight-16DE report matched that unit. No new BLE/USB connection, firmware
flash or bridge restart was started by this diagnosis.

Read-only registry inspection found one anonymous codex:proc_<appPID> Y record
approximately 4,070 seconds old plus this coordinator's current real conversation
Y. The installed ~/.local/share/trafficlights/traffic.py still used the old
process-parent fallback; the repository had a tested stable-identity correction
which had not yet been deployed into that installed copy.

22 hook-runtime tests passed. The installed observer was atomically replaced at
the same stable path with the tested source, preserving a private prior-copy
backup. ~/.codex/hooks.json content hash remained unchanged; trust, permissions,
provider configuration and bridge/hardware services were not modified. Only the
identified anonymous stale record was removed with its session-scoped O command.
No global clearing or artificial completion of actual chats was performed.

Verification: zero anonymous working records, one legitimate coordinator turn;
board report remained Y / 1 WIP during that actual turn, as expected. Its ordinary
Stop hook should take it to zero/green after the reply. Post-reply visible idle
confirmation remains owner-dependent. This is a host record/hook-runtime fix,
not physical LED, firmware or cross-provider acceptance. ESP32 test unit had been
unplugged and was not accessed. The owner subsequently authorized committing and pushing this fix.

## Owner confirmation

The owner explicitly confirmed: "It’s green now." This verifies visible return
to idle green after the actual coordinator turn finished. The source fix,
regression tests and these findings are included in the authorized commit.
