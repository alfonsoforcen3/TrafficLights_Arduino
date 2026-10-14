# Working-provider OLED icons — 2026-10-13

Added hook-namespace working-provider detection, bounded BLE P<mask> metadata,
fragment-safe parser support, and provider-specific 36-pixel monochrome marks.
Claude uses the existing proportional Clawdy animation, Codex the OpenAI mark,
Gemini a code-drawn four-point star, and unknown providers a neutral symbol.
Mixed providers rotate on the existing five-second phrase interval. Title,
WIP footer, GPIOs and full green duty remain intact. Only Y sessions count.
No active providers/disconnection returns to the Clawdy companion.

OpenAI asset source: official openai/openai-cookbook repository,
examples/voice_solutions/realtime_translation_guide/livekit-translation-demo/
public/brand/chatgpt-blossom-white.svg, retrieved 2026-10-13. Source SVG was
rasterized into a 36x36 monochrome row mask. The logo and screen-composite
previews were visually inspected for layout; source art is an identification
mark, not a new mascot or modified trademark.

Forty-five hardware-free tests passed. Coverage includes mixed-provider
filtering, exclusion of completed/waiting sessions, all provider-mask render
combinations, neutral fallback, glyph fit, metadata packet fragmentation,
malformed metadata isolation, disconnect reset, and firmware dependency order.
Board identity nice_nano / CircuitPython 8.1.0 / UID suffix 16DE confirmed before
writes. Preserved all existing files/profile in ignored backup. No boot.py,
UF2, bootloader or hooks/trust changes. Refreshed Mac bridge using --no-hooks
with verified TrafficLight-16DE name; BLE connected and OLED reported no error.

Baseline real local Codex hook namespace reported provider mask 2 and one working
session. Isolated synthetic Claude/Gemini namespace sessions were added, completed
and removed to verify working mask/count delivery; these tests do not establish
actual Claude or Gemini lifecycle dispatch. Existing user sessions were retained.
BLE acknowledgements passed masks/counts 2/1 → 3/2 → 7/3 → 6/2 → 2/1, with oled_error=null throughout.

Pending: owner visual confirmation of provider switching, real Claude/Gemini
application dispatch, physical power cycling, sleep/wake, Mac restart, extended
runtime and Windows acceptance. Ordinary browser-chat/model detection remains
unsupported. No new providers installed. Changes remain uncommitted.

## Top WIP layout correction

Owner requested WIP in the OLED yellow band, smaller graphics underneath, and
the separator unchanged. Moved WIP text to y=2; provider marks now 30x30 at
y=18, with their labels below. Clawdy uses a uniform 75% drawing transform with
its expressions and effects below the yellow band. Separator remains x=49,
y=10 through 55. Eight OLED tests passed, including all states/providers,
four-digit WIP fitting, clear band below WIP, and exact separator pixels.
A composite preview was visually inspected, then the board module was backed
up and updated. OLED color is physically fixed by its bands, not software
selectable. Owner visual acceptance pending.

Owner requested both headers at the top and a larger Clawdy title. WIP now
starts at y=0 and Clawdy uses 2x glyphs at x=56/y=0 (70x14 pixels), entirely
inside the yellow band. Status comments, smaller graphics and separator are
retained. Eight OLED tests passed; preview visually inspected; backed up the
board module and deployed. Visual approval pending.
