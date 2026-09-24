#!/usr/bin/env python3
"""
bridge.py — Persistent background serial bridge daemon for Arduino Traffic Light.

Keeps the serial connection to the Arduino open so that CLI hooks can send
state updates instantaneously without causing the Arduino to auto-reset on every command.
Listens for commands ('R', 'B', 'Y', 'G', 'O', 'T') on 127.0.0.1:8765 (TCP).
"""

import sys
import glob
import socket
import time
import serial

import serial.tools.list_ports

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765
BAUD_RATE = 115200

def find_serial_port():
    override = os.environ.get("TRAFFIC_PORT")
    if override:
        return override
    ports = list(serial.tools.list_ports.comports())
    # 1. Prefer Arduino / CH340 / USB-Serial devices
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "1a86:7523" in hwid or "ch340" in desc or "arduino" in desc or "usb" in desc or "serial" in desc:
            return p.device
    # 2. Return COM ports on Windows or usb ports on POSIX
    for p in ports:
        if p.device.upper().startswith("COM") or "usb" in p.device.lower():
            return p.device
    return ports[0].device if ports else None

def run_bridge():
    port = find_serial_port()
    if not port:
        print("❌ Error: No Arduino serial port found (/dev/cu.usbserial* or /dev/cu.usbmodem*).", file=sys.stderr)
        sys.exit(1)

    print(f"🔌 Connecting to Arduino on {port} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        # Give Arduino bootloader 1.8s to finish setup on initial connection
        time.sleep(1.8)
        if ser.in_waiting:
            ser.read(ser.in_waiting)
        # Set to green to indicate ready
        ser.write(b'G')
        print(f"✅ Arduino Traffic Light Bridge is READY! Listening on {TCP_HOST}:{TCP_PORT}...")
    except Exception as e:
        print(f"❌ Failed to open serial port {port}: {e}", file=sys.stderr)
        sys.exit(1)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(5)

    try:
        while True:
            client, _ = server.accept()
            try:
                data = client.recv(16)
                cmd = data.decode("utf-8", errors="ignore").strip().upper()
                if cmd in ('R', 'B', 'Y', 'G', 'O', 'T'):
                    ser.write(cmd.encode("utf-8"))
                    ser.flush()
                    print(f"🚦 Command applied: {cmd}")
                client.sendall(b"OK\n")
            except Exception as e:
                print(f"Client communication error: {e}", file=sys.stderr)
            finally:
                client.close()
    except KeyboardInterrupt:
        print("\nStopping bridge...")
    finally:
        try:
            ser.write(b'O')
            ser.close()
            server.close()
        except Exception:
            pass

if __name__ == "__main__":
    run_bridge()
