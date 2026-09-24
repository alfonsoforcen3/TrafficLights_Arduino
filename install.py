#!/usr/bin/env python3
"""
install.py — One-Shot Automated AI Installer for Arduino Traffic Light.

Designed for autonomous AI agents and humans alike.
Automatically:
1. Installs Python dependencies (pyserial).
2. Detects the Arduino USB COM/serial port.
3. Configures and registers lifecycle hooks with full local paths.
4. Starts the persistent background bridge daemon (cross-platform).
5. Runs a quick self-test confirming hardware readiness.

Usage:
  python install.py
"""

import os
import sys
import time
import socket
import platform
import subprocess

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
BRIDGE_SCRIPT = os.path.join(SCRIPTS_DIR, "bridge.py")
TRAFFIC_SCRIPT = os.path.join(SCRIPTS_DIR, "traffic.py")
MANAGE_SCRIPT = os.path.join(PROJECT_DIR, "manage_hooks.py")

def step(title):
    print(f"\n👉 {title}...")

def install_dependencies():
    step("Step 1: Checking and installing Python dependencies")
    try:
        import serial
        import serial.tools.list_ports
        print("✅ pyserial is already installed.")
    except ImportError:
        print("📦 Installing pyserial...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
        print("✅ pyserial installed successfully.")

def detect_hardware():
    step("Step 2: Detecting Arduino hardware")
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    arduino_port = None
    # 1. Prefer known Arduino / CH340 / USB serial devices
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "1a86:7523" in hwid or "ch340" in desc or "arduino" in desc or "usb" in desc or "serial" in desc:
            arduino_port = p.device
            break

    if not arduino_port and ports:
        for p in ports:
            if p.device.upper().startswith("COM") or "usb" in p.device.lower():
                arduino_port = p.device
                break

    if arduino_port:
        print(f"🔌 Found Arduino on port: {arduino_port}")
        return arduino_port
    else:
        print("⚠️  Warning: No Arduino serial/COM port detected right now.")
        print("   Please make sure the Arduino is plugged in via a USB data cable.")
        return None

def enable_hooks():
    step("Step 3: Registering lifecycle hooks")
    subprocess.check_call([sys.executable, MANAGE_SCRIPT, "enable"])

def is_bridge_running():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        sock.connect(("127.0.0.1", 8765))
        sock.close()
        return True
    except Exception:
        return False

def start_background_bridge():
    step("Step 4: Starting background bridge daemon")
    if is_bridge_running():
        print("✅ Serial bridge is already running.")
        return

    is_windows = platform.system() == "Windows"
    log_file = os.path.join(PROJECT_DIR, "bridge.log")

    if is_windows:
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        with open(log_file, "a") as out:
            subprocess.Popen(
                [sys.executable, BRIDGE_SCRIPT],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                stdout=out,
                stderr=out,
                close_fds=True
            )
    else:
        with open(log_file, "a") as out:
            subprocess.Popen(
                [sys.executable, BRIDGE_SCRIPT],
                stdout=out,
                stderr=out,
                start_new_session=True
            )

    # Wait up to 4 seconds for bridge to bind to port 8765
    for _ in range(8):
        time.sleep(0.5)
        if is_bridge_running():
            print("✅ Background bridge started successfully.")
            return

    print("🟡 Bridge launched (initial handshake in progress).")

def verify_and_test():
    step("Step 5: Verifying traffic light state")
    try:
        subprocess.check_call([sys.executable, TRAFFIC_SCRIPT, "G"])
        print("🟢 Traffic light set to GREEN (Ready / Standby).")
    except Exception as e:
        print(f"⚠️ Test command returned: {e}")

def main():
    print("=" * 60)
    print("🚦 ARDUINO TRAFFIC LIGHT — AUTOMATED AI INSTALLER")
    print(f"   OS: {platform.system()} ({platform.machine()})")
    print(f"   Project Directory: {PROJECT_DIR}")
    print("=" * 60)

    install_dependencies()
    detect_hardware()
    enable_hooks()
    start_background_bridge()
    verify_and_test()

    print("\n" + "=" * 60)
    print("🎉 INSTALLATION COMPLETE!")
    print("   The traffic light is now active and monitoring all AI sessions.")
    print("   - Yellow: Thinking / Working")
    print("   - Blinking Red: User Input Required")
    print("   - Solid Red: Error / Blocked")
    print("   - Green: Ready / Standby")
    print("   To revert or disable at any time: python manage_hooks.py disable")
    print("=" * 60)

if __name__ == "__main__":
    main()
