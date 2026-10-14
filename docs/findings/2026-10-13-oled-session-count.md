# OLED session count — 2026-10-13

Added numeric tracked-session metadata to the BLE heartbeat, a bounded
incremental board parser, and a right-column CHATS header above existing status
comments. Clawdy's proportions, reactions, GPIO profile and full green duty are
retained. No provider hooks, trust settings, transcripts, or session identifiers
are forwarded or changed by this update.

Verified hardware identity via boot_out.txt before application writes:
nice_nano, CircuitPython 8.1.0, UID suffix 16DE. Existing files/profile preserved
in an ignored local backup. Copied dependencies before code.py without changing
boot.py or flashing UF2/bootloader. Updated Mac helper with install.py --no-hooks
and the board's previously verified name TrafficLight-16DE.

Thirty-nine hardware-free tests passed, including fragmented metadata,
malformed metadata isolation, disconnect reset, legacy commands, missing OLED,
unknown/zero/singular/large headers and animation rendering. BLE reconnected;
firmware transport=ble acknowledged session_count=15 matching the host registry,
with oled_error=null. This initial registry included ready chats; the count
means tracked chats, not only busy turns. Synthetic add/close count transitions
were tested using isolated session IDs; only those test records were removed.

Visual header confirmation remains pending. Real session lifecycle depends on
provider dispatch and session-end events; abandoned records can persist until
the existing 24-hour expiry. Updates follow the three-second heartbeat plus BLE
and rendering latency; no instantaneous-update claim. Physical power cycles,
Mac reboot, prolonged runtime and Windows acceptance were not performed for this
iteration. Changes remain uncommitted.

## Owner correction: working-only count and drawing footer

The owner requested working sessions only, beneath Clawdy, with `Clawdy` as the
right-column title. This supersedes the tracked-total/header layout above.
The BLE callback now counts only Y states; G/B/R are excluded. The title uses
mixed-case glyphs and remains fixed while the count changes. Two rows beneath
the figure show the number and WORKING, with -- for unknown/disconnected data.
Firmware reports session_count_kind=working. Forty tests passed, including
mixed-provider working-state filtering, completion/wait transitions, and footer
changes with unchanged title pixels. Updated the Mac bridge with --no-hooks;
no trust settings were modified. Visual layout approval remains pending.

Owner requested a compact one-line footer: replaced number/WORKING rows with
`N WIP`, centered below Clawdy at y=54. Even `9999 WIP` fits the 49-pixel left
column (47 pixels at the existing font size). Four OLED tests passed, including
large-count rendering; deployed without changing host count semantics.

Owner requested funny status statements. Deployed yellow BRAIN GO / BRRR...;
green NAILED IT! / SNACK TIME; red OH CRUMBS! / SEND HELP; waiting for input
YOUR TURN! / HUMAN!; idle ON A BREAK / GOT SNACKS?; disconnected HELLO? /
ANYONE HOME?. Added required punctuation/M glyphs. Longest line is 12
characters (71 pixels), fitting the 72-pixel right text area. Four OLED render
tests passed across statuses/disconnection. Clawdy title, WIP footer, animations
and count semantics retained. Visual text approval pending.

Added four funny phrase pairs per status, including disconnected, rotating every
five seconds of monotonic elapsed time. Status changes reset to their first
phrase; heartbeat and WIP-count changes do not restart rotation. Six OLED tests
passed, covering all 24 pairs, glyph availability/column width, wraparound,
elapsed-time selection and status resets. Deployed with original OLED module
backed up. Animations/title/footer retained. Visual rotation approval pending.
