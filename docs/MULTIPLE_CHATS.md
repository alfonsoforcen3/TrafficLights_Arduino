# Multiple chats and settled display states

One Mac bridge and one board serve all supported local chats. Each hook sends a conversation/session ID plus its latest state. The bridge stores separate records, so finishing one chat does not mark another finished. The board receives only the combined colour, not prompts, chat titles, or a list of conversations.

## Priority

| Highest active signal | Display |
| --- | --- |
| Any chat requests input/permission (B) | Blinking red, after 0.8 seconds |
| Otherwise any chat has an explicit error (R) | Solid red immediately |
| Otherwise any chat is working (Y) | Amber immediately |
| Otherwise all chats are ready/finished, or none are tracked (G) | Green after 1.5 seconds when transitioning |

Examples: A working + B finished stays amber. A working + B waiting for permission becomes blinking red. A finished + B working stays amber. When both finish, green follows the completion settling delay. An input signal has priority even over another chat's error.

Each chat's latest event replaces its own previous state. Later work clears that chat's input/error signal; Stop/Interrupt marks it ready; SessionEnd removes only that chat. Error red is an explicit signal, not a guarantee that every failed shell command is detected. The input light reflects hooks, not independent polling of every pending question; a subsequent work event in the same chat can clear it.

## Transition timing

Amber and solid error red are immediate. Green waits for the aggregate to stay finished/ready for 1.5 seconds. New work or another higher-priority signal cancels the pending green transition. Blinking red waits 0.8 seconds and is cancelled if the input signal clears sooner. Repeated events for the same pending colour do not restart its timer. These delays smooth state changes; they do not fade LED brightness. Factory/diagnostic colour tests bypass settling and intentionally cycle colours.

Green means all tracked hooks report ready/finished. The indicator cannot determine hidden model work outside supported local hooks. Board startup also defaults to green before the host reconnects, so green alone does not prove a live connection.

## Recovery and limitations

Records are persisted in ~/.local/share/trafficlights/sessions.json. Helper restart restores valid records younger than 24 hours; older records expire. Abruptly closed chats with no final hook can leave stale amber/red. `python3 manage_hooks.py status` lists tracked session states and Bluetooth/GPIO status. `python3 manage_hooks.py reset` clears every chat record; use it for abandoned sessions, not while other chats are working.

Normal supported hooks supply a stable session ID. Missing IDs fall back to the hook process's parent ID; integrations without stable IDs are not verified for correct multi-chat accounting. Ordinary ChatGPT web chats and cloud-orchestrated work do not automatically enter this local registry. Multiple Macs controlling one board and multiple-board routing are not implemented.
