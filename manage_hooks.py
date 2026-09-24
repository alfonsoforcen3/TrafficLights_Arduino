#!/usr/bin/env python3
"""
manage_hooks.py — Safe Hook Manager for Gemini / Antigravity CLI.

Allows enabling, disabling (reverting), checking status, and testing the
traffic light hooks with zero risk to your existing configurations.

Usage:
  python3 manage_hooks.py enable    # Enables hooks (automatically creates backup)
  python3 manage_hooks.py disable   # Completely removes/reverts hooks
  python3 manage_hooks.py status    # Checks current hook & hardware status
  python3 manage_hooks.py test      # Cycles all lights to verify operation
"""

import os
import sys
import json
import shutil
import datetime
import subprocess

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
TRAFFIC_SCRIPT = os.path.join(SCRIPTS_DIR, "traffic.py")

# Global Antigravity / Gemini config directory
CONFIG_DIR = os.path.expanduser("~/.gemini/config")
HOOKS_FILE = os.path.join(CONFIG_DIR, "hooks.json")
BACKUP_DIR = os.path.join(PROJECT_DIR, ".backups")

# The exact hook definition
TRAFFIC_HOOK_DEF = {
    "enabled": True,
    "PreInvocation": [
        {
            "type": "command",
            "command": f"python3 {TRAFFIC_SCRIPT} Y"
        }
    ],
    "PostInvocation": [
        {
            "type": "command",
            "command": f"python3 {TRAFFIC_SCRIPT} G"
        }
    ],
    "Stop": [
        {
            "type": "command",
            "command": f"python3 {TRAFFIC_SCRIPT} G"
        }
    ]
}

def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_file(filepath):
    if not os.path.exists(filepath):
        return None
    ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"hooks_{timestamp}.json.bak")
    shutil.copy2(filepath, backup_path)
    return backup_path

def enable_hooks():
    print("🚦 Enabling Traffic Light Hooks...")
    os.makedirs(CONFIG_DIR, exist_ok=True)

    data = {}
    if os.path.exists(HOOKS_FILE):
        bak = backup_file(HOOKS_FILE)
        if bak:
            print(f"📦 Created backup of existing config: {bak}")
        try:
            with open(HOOKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["traffic-light"] = TRAFFIC_HOOK_DEF

    with open(HOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Hooks successfully written to: {HOOKS_FILE}")
    print("🚦 Sending Green (Ready) signal to Arduino...")
    subprocess.run([sys.executable, TRAFFIC_SCRIPT, "G"])
    print("\n🎉 Done! The traffic light will now automatically track your sessions.")
    print("👉 To revert/disable at any time, simply run: python3 manage_hooks.py disable")

def disable_hooks():
    print("🛑 Disabling / Reverting Traffic Light Hooks...")
    if not os.path.exists(HOOKS_FILE):
        print(f"ℹ️  No {HOOKS_FILE} found. Hooks are already not active.")
        return

    bak = backup_file(HOOKS_FILE)
    if bak:
        print(f"📦 Backup saved before reverting: {bak}")

    try:
        with open(HOOKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    if "traffic-light" in data:
        del data["traffic-light"]
        print("🗑️  Removed 'traffic-light' hook from configuration.")

    # If data is now empty, we can remove the file entirely or write empty dict
    if not data:
        os.remove(HOOKS_FILE)
        print(f"🧹 {HOOKS_FILE} is now empty and was safely removed.")
    else:
        with open(HOOKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Other custom hooks were preserved in {HOOKS_FILE}.")

    # Turn off the traffic light
    subprocess.run([sys.executable, TRAFFIC_SCRIPT, "O"])
    print("⚫ Sent OFF signal to Arduino.")
    print("\n✅ Successfully reverted! No active traffic light hooks remain.")

def check_status():
    print("🔍 --- TRAFFIC LIGHT HOOK STATUS ---")
    
    # 1. Config file
    if os.path.exists(HOOKS_FILE):
        try:
            with open(HOOKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "traffic-light" in data and data["traffic-light"].get("enabled", True):
                print(f"🟢 Hook Status: ACTIVE in {HOOKS_FILE}")
            else:
                print(f"🟡 Hook Status: Config file exists, but 'traffic-light' is disabled/missing.")
        except Exception as e:
            print(f"⚠️  Hook Status: Error reading {HOOKS_FILE}: {e}")
    else:
        print(f"⚪ Hook Status: INACTIVE (No {HOOKS_FILE})")

    # 2. Bridge process
    bridge_running = False
    try:
        out = subprocess.check_output(["ps", "aux"]).decode("utf-8")
        for line in out.splitlines():
            if "bridge.py" in line and "grep" not in line:
                bridge_running = True
                break
    except Exception:
        pass

    if bridge_running:
        print("🟢 Serial Bridge: RUNNING (0ms latency mode)")
    else:
        print("🟡 Serial Bridge: STOPPED (Operating in direct-serial fallback mode)")

    # 3. Serial Port
    ports = [p for p in os.listdir("/dev") if p.startswith("cu.usbserial") or p.startswith("cu.usbmodem")]
    if ports:
        print(f"🔌 Hardware Port: Connected ({', '.join(['/dev/' + p for p in ports])})")
    else:
        print("❌ Hardware Port: No Arduino USB device detected in /dev/cu.*")

def run_test():
    print("🚦 Running light test cycle...")
    for color, name in [("R", "🔴 Red"), ("Y", "🟡 Yellow"), ("G", "🟢 Green"), ("O", "⚫ Off")]:
        print(f"Switching to {name}...")
        subprocess.run([sys.executable, TRAFFIC_SCRIPT, color])
        subprocess.run(["sleep", "1"])
    print("✅ Test cycle complete!")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "enable":
        enable_hooks()
    elif cmd in ("disable", "revert"):
        disable_hooks()
    elif cmd == "status":
        check_status()
    elif cmd == "test":
        run_test()
    else:
        print(f"Unknown command: '{cmd}'. Use: enable, disable, status, or test.")
        sys.exit(1)

if __name__ == "__main__":
    main()
