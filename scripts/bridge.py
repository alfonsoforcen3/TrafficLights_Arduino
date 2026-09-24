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

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765
BAUD_RATE = 115200

def find_serial_port():
    ports = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.usbmodem*")
    return ports[0] if ports else None

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
