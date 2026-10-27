# macOS child-pipe fixture correction — 27 October 2026

## Trigger and evidence

PR #1 at `cfda889` built the native Mac prototype, then failed
`real child small ack delivered`. Its other six checks passed. A retry produced
the same assertion. The current default branch had previously passed its checks;
the native source was identical between these branches.

The old fixture launches `/usr/bin/python3` and includes its cold startup in a
one-second response deadline. It also stops at the first nonempty pipe chunk
rather than waiting for a complete newline-delimited frame. Controlled baseline
runs passed normally (0.927 s), failed with an injected 1.2 s startup delay
(1.705 s), and failed with an intentionally fragmented reply (0.892 s).
Both injections reproduced the reported assertion independently. The exact
trigger on the GitHub runner was not observed; the assertion alone does not
identify which assumption failed there.

## Correction

The self-test launches its own native executable in an early test-only helper
mode. An explicit readiness handshake has a separate bounded five-second startup
budget. The existing one-second response budget begins after readiness.
The helper sends only `{`, then waits until the parent receives that fragment
before releasing the rest of the pong. The parent uses the production NDJSON
framer and decodes an exact typed pong/nonce, while verifying the child still
owns an open stdout pipe. Startup delays of 0 and 1200 ms are both exercised.
Owned child cleanup is bounded. Invalid helper arguments exit before normal
application startup. Production pipe reading, framing, watchdogs and UI behavior
were not changed.

## Local verification

- Isolated signed native build passed; host, attention and renderer self-tests
  passed. Five additional host runs passed (each tests immediate/delayed startup
  and forced fragmentation). A final guarded build passed all three flags again.
- Independent specialist review approved the design. Direct helper QA passed
  immediate/delayed startup, wrong token and EOF after ready/prefix/pong; exact
  frames arrived within the response budget and children stayed alive until
  release. Invalid helper delay values exited with status 2.
- All 273 hardware-free repository regression tests passed (13.034 seconds).
- The owner's visible trial, hooks, startup, privacy/trust settings and hardware
  integrations were not restarted or altered by these fixture tests.

Hosted CI must verify the committed correction. This is test reliability
evidence, not native UI, real-provider or physical-device acceptance.
