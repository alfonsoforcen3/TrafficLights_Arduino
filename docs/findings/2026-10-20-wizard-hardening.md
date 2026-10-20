# Wizard hardening and virtual companion planning

Private working iteration, 20 October 2026, based on `512ecc8`.

Daniel implemented wizard hardening; Rafael performed independent read-only
failure-path review; Leo authored the [Virtual Clawdy plan](../VIRTUAL_CLAWDY_PLAN.md).
Alex reviewed their reports and integrated customer documentation.

## Changes and evidence

- Both wizard entry points handle EOF, Ctrl-C and backend errors without an
  unhandled traceback. Invalid names/options fail before setup side effects.
- BLE discovery has an outer deadline with cleanup allowance; notifications
  discard oversized/malformed frames and identification queues are bounded.
  Strict UID/capability/acknowledgement validation preserves older keep-name
  firmware while refusing unsupported renames.
- Dependency preparation and the direct installer have deadlines. A per-unit
  private recovery record precedes rename/install, distinguishes uncertain
  rename from confirmed rename and installation phases, and gives retry advice.
  Windows retry instructions quote literal PowerShell arguments; POSIX shells
  use shell-safe argument quoting. Nothing automatically resumes or rolls back.
- LED verification checks the selected UID and BLE peer throughout, validates
  GPIO evidence, and preserves the first failure if restoring tracking also fails.

Integrated check: **179 hardware-free tests passed in 6.824 seconds** using the
existing runtime venv. Tests use mocked Bluetooth/socket transactions and
temporary recovery/configuration paths. The initial system-Python run failed
four imports because that interpreter lacked Bleak; rerunning with the existing
dependency environment passed. No dependencies were installed for verification.
Peer review caught and corrected a discovery deadline equal to the scan duration
and PowerShell expansion in retry commands before final validation.
The documented offline preview passed without BLE or setup side effects;
whitespace and all changed-document local links passed. The full documentation
checker stalled reading the unrelated `docs/TROUBLESHOOTING.md` from this
Desktop checkout and was stopped; no full-repository documentation pass is
claimed for this iteration.

## Limits

Run only one wizard per laptop/runtime; no concurrency lock is implemented.
Async deadlines depend on backend cancellation cooperation. Stopping the direct
installer does not prove descendants, an installed service or prior hook changes
were removed. Recovery records are guidance, not atomic device/host transactions;
no power-loss-safe rename or rollback is claimed. Provider trust review remains
manual. Physical customer onboarding and native Windows acceptance remain pending.

No real toy connection, firmware update, live integration change, public release,
commit or push was performed in this iteration. The virtual app is a detailed
design only; performance budgets and crash-recovery gates are proposed tests,
not measured product guarantees. Generated candidate archives from the previous
iteration have not been rebuilt and do not include these changes.
