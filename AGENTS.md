# Instructions for AI Agents 🤖

You are an AI developer or agent running on this machine (Windows, macOS, or Linux).
The user wants you to install and set up this Arduino Traffic Light system.

---

## ⚡ Automated Installation (Run this command)

To install this tool completely, run the following command from the root of this repository:

```bash
python install.py
```
*(On systems where Python 3 is mapped to `python3`, use `python3 install.py`).*

### What `install.py` does automatically:
1. Installs the `pyserial` dependency if not already installed.
2. Auto-detects the connected Arduino COM/serial port (cross-platform).
3. Registers the lifecycle hooks into the user's AI environment (`~/.gemini/config/hooks.json` or equivalent) using absolute local paths for this machine.
4. Starts the background bridge daemon (`bridge.py`) so communication has 0ms latency without resetting the Arduino board.
5. Runs a test and lights the LED **Green** (Ready / Standby).

---

## 🛑 How to Revert or Uninstall

If the user asks you to remove, disable, or uninstall the traffic light:
```bash
python manage_hooks.py disable
```
This cleanly removes the hooks, restores previous configuration backups, and leaves no residual files.

---

## 🔍 How to Check Status

To diagnose or verify hardware and hooks:
```bash
python manage_hooks.py status
```
