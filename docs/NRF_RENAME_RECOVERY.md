# nRF persistent rename: interrupted-write recovery

This private candidate uses one checked 40-byte record at `microcontroller.nvm`
offsets 0–39. It is not an atomic transaction. No physical power-interruption or
recovery test has been completed on the pinned CircuitPython/board profile.

If power is lost during the first rename, the marker can be only partly written.
After restart, a nonempty region lacking the complete `CLN1` marker is treated as
foreign: `rename_supported=false`, with the configured factory BLE name (or the
UID-based default) retained. A customer retry cannot repair that region. A complete
marker with an invalid payload falls back to the factory name but can still allow
a new checked rename. If the write completed but its acknowledgement was lost,
inspect Q and the advertised name before assuming persistence failed.

## Factory-only handling

1. Record the exact unit ID, factory BLE label, board and CircuitPython versions.
   Preserve `hardware_config.json`, firmware and a complete NVM snapshot before
   any service write. Keep the unit on stable, authorized service power.
2. Compare the suspect region with the unit's pre-enrollment NVM snapshot and
   allocation records. A partial marker alone cannot prove ownership. If the
   factory cannot prove offsets 0–39 were reserved for this feature, stop: retain
   the contents and use the supported keep-name path or a service replacement.
3. Only after establishing that allocation, factory service may replace this
   feature's 40-byte region with an empty record, preserving every byte outside
   it. Never erase all NVM, other records, the filesystem or per-unit configuration.
   The underlying flash operation is not power-loss atomic; the full snapshot is
   needed even for this limited write. No automatic erase/recovery command is
   provided by customer onboarding.
4. Read back the region and confirm all bytes outside it and the hardware profile
   are unchanged. Restart, query the same immutable identity, and check rename
   capability. Repeat rename, cold-power persistence, BLE/visible LED and actual
   provider checks before returning the unit. Record pass/fail/not-run evidence.

This procedure documents the recovery boundary; it does not qualify the single
record design for production power-loss durability. Customer software must not
silently erase unknown NVM or claim an interrupted rename was successful.
