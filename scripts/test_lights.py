#!/usr/bin/env python3
"""
test_lights.py — Interactive hardware test runner for Arduino Traffic Light.

Tests each LED individually (Green=Pin 9, Yellow=Pin 10, Red=Pin 11)
and provides an interactive prompt to toggle states.
"""

import sys
import time
import serial
import serial.tools.list_ports

def find_serial_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "1a86:7523" in hwid or "ch340" in desc or "arduino" in desc or "usb" in desc or "serial" in desc:
            return p.device
    for p in ports:
        if p.device.upper().startswith("COM") or "usb" in p.device.lower():
            return p.device
    return ports[0].device if ports else None

def main():
    port = find_serial_port()
    if not port:
        print("❌ No Arduino serial port detected!")
        print("Please check that your Arduino USB cable is plugged in.")
        sys.exit(1)

    print(f"🔌 Connecting to Arduino on {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print("⏳ Waiting for Arduino bootloader to initialize (2 seconds)...")
        time.sleep(2)
        
        # Read any startup banner
        if ser.in_waiting:
            banner = ser.read(ser.in_waiting).decode("utf-8", errors="ignore").strip()
            print(f"📟 Arduino Banner: {banner}")

        print("\n🚦 --- STEP 1: AUTOMATED HARDWARE CYCLE ---")
        
        print("🔴 Testing RED (Digital Pin 11)...")
        ser.write(b'R')
        ser.flush()
        time.sleep(1.2)

        print("🟡 Testing YELLOW (Digital Pin 10)...")
        ser.write(b'Y')
        ser.flush()
        time.sleep(1.2)

        print("🟢 Testing GREEN (Digital Pin 9)...")
        ser.write(b'G')
        ser.flush()
        time.sleep(1.2)

        print("⚫ Turning OFF...")
        ser.write(b'O')
        ser.flush()
        time.sleep(0.5)

        print("\n✅ Automated test complete!")
        print("\n🎮 --- STEP 2: INTERACTIVE CONTROLLER ---")
        print("Keys: [R] Red  |  [Y] Yellow  |  [G] Green  |  [O] Off  |  [T] Test  |  [Q] Quit")

        while True:
            choice = input("Enter command: ").strip().upper()
            if not choice:
                continue
            if choice == 'Q':
                ser.write(b'O')
                print("Exiting.")
                break
            elif choice in ('R', 'Y', 'G', 'O', 'T'):
                ser.write(choice.encode('utf-8'))
                ser.flush()
                color_names = {'R': '🔴 RED', 'Y': '🟡 YELLOW', 'G': '🟢 GREEN', 'O': '⚫ OFF', 'T': '✨ TEST CYCLE'}
                print(f"Sent: {color_names.get(choice)}")
            else:
                print("Unknown command. Use R, Y, G, O, T, or Q.")

        ser.close()

    except Exception as e:
        print(f"\n❌ Serial Communication Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
