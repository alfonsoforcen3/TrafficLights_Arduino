# 🚦 Hook Configuration & Reversion Guide

This guide explains how lifecycle hooks connect your AI sessions to the physical Arduino traffic light, and how you can safely enable, disable, or completely revert them at any time.

---

## ⚡ Quick Controls (One-Line Commands)

A dedicated manager script [`manage_hooks.py`](manage_hooks.py) is provided to make toggling completely painless and safe:

### 1. Enable Hooks
```bash
./manage_hooks.py enable
```
* Automatically creates a backup of your configuration before making any changes.
* Connects `PreInvocation` (Yellow), `PostInvocation` (Green), and `Stop` (Green).
* Turns your traffic light Green (Ready).

### 2. Revert / Disable Hooks
```bash
./manage_hooks.py disable
```
* Removes the `traffic-light` hooks immediately.
* Preserves any other custom hooks you may have.
* Automatically cleans up the file if no other hooks exist.
* Turns the light Off.

### 3. Check Current Status
```bash
./manage_hooks.py status
```
* Displays whether hooks are currently active, whether the 0ms background serial bridge is running, and your Arduino port connection.

### 4. Test Lights
```bash
./manage_hooks.py test
```
* Cycles Red ➔ Yellow ➔ Green ➔ Off to verify all LEDs.

---

## 🔍 How It Works Under the Hood

When you enable hooks, a single entry is added to `~/.gemini/config/hooks.json`:

```json
{
  "traffic-light": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python3 /Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/scripts/traffic.py Y"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 /Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/scripts/traffic.py G"
      }
    ]
  }
}
```

### Lifecycle Mapping:
1. **`PreInvocation`** (Prompt submitted / Thinking): Calls `traffic.py Y` ➔ **🟡 Yellow LED lights up**. Stays solid throughout all intermediate tool calls.
2. **`Input Needed`** (Awaiting user reply / Permission): Calls `traffic.py B` ➔ **🚨 Blinking Red LED**.
3. **`Error / Failure`** (Tool failed or crashed): Calls `traffic.py R` ➔ **🔴 Solid Red LED**.
4. **`Stop`** (Model turn fully completes): Calls `traffic.py G` ➔ **🟢 Green LED lights up**.
5. **`manage_hooks.py disable`**: Calls `traffic.py O` ➔ **⚫ LEDs turn off**.

---

## 🛡️ Manual Reversion (If you ever prefer doing it by hand)

If you ever want to revert manually without using the script:

1. Open `~/.gemini/config/hooks.json` in any text editor.
2. Either delete the `"traffic-light": { ... }` block, or set `"enabled": false`:
   ```json
   "traffic-light": {
     "enabled": false,
     ...
   }
   ```
3. If `hooks.json` only contained the traffic light hook, you can delete the file completely:
   ```bash
   rm ~/.gemini/config/hooks.json
   ```
4. Backups are stored in [`/Users/alfonsoforcen3/Desktop/TrafficLights_Arduino/.backups/`](.backups/).

---

## 🔌 Background Bridge (`bridge.py`)

* Arduinos naturally reboot when an operating system opens a serial port.
* To prevent this reboot on every prompt and provide **instant (<2ms) transitions**, [`scripts/bridge.py`](scripts/bridge.py) runs as a lightweight daemon keeping the USB port open.
* If you ever want to stop the bridge daemon:
  ```bash
  pkill -f bridge.py
  ```
  *(Even if stopped, `traffic.py` automatically falls back to direct USB communication).*
