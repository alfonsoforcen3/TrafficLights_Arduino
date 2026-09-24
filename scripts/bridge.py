#!/usr/bin/env python3
"""
bridge.py — Persistent Multi-Session Serial Bridge Daemon for Arduino Traffic Light.

Maintains an in-memory session registry for all concurrent AI CLI sessions
and applies Priority Resolution:
  1. 🚨 Blinking Red ('B'): If ANY session needs user input/permission
  2. 🔴 Solid Red ('R'):    If ANY session encountered an error
  3. 🟡 Solid Yellow ('Y'): If ANY session is currently working/thinking
  4. 🟢 Solid Green ('G'):  When ALL active sessions are finished/ready
  5. ⚫ Off ('O'):          When all sessions have ended

Listens on TCP 127.0.0.1:8765.
Accepts JSON commands and status queries.
"""

import os
import sys
import json
import time
import socket
import serial
import serial.tools.list_ports

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765
BAUD_RATE = 115200

# Registry: { session_id: { "state": 'Y'|'G'|'R'|'B'|'O', "updated": timestamp } }
active_sessions = {}
current_hardware_state = 'G'

def find_serial_port():
    override = os.environ.get("TRAFFIC_PORT")
    if override:
        return override
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

def compute_aggregate_state():
    """Calculates highest-priority state across all tracked sessions."""
    if not active_sessions:
        return 'G'

    states = [s["state"] for s in active_sessions.values()]

    # 1. Top priority: Any session needs user input/confirmation
    if 'B' in states:
        return 'B'
    # 2. Second priority: Any session in error state
    if 'R' in states:
        return 'R'
    # 3. Third priority: Any session working/thinking
    if 'Y' in states:
        return 'Y'
    # 4. Standby: All active sessions ready
    if 'G' in states:
        return 'G'

    return 'O'

def clean_stale_sessions():
    """Cleans up sessions inactive for over 12 hours."""
    now = time.time()
    stale = [sid for sid, s in active_sessions.items() if now - s["updated"] > 43200]
    for sid in stale:
        del active_sessions[sid]

def run_bridge():
    global current_hardware_state
    port = find_serial_port()
    if not port:
        print("❌ Error: No Arduino serial port found.", file=sys.stderr)
        sys.exit(1)

    print(f"🔌 Connecting to Arduino on {port} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(1.8)
        if ser.in_waiting:
            ser.read(ser.in_waiting)
        ser.write(b'G')
        current_hardware_state = 'G'
        print(f"✅ Multi-Session Arduino Bridge READY! Listening on {TCP_HOST}:{TCP_PORT}...")
    except Exception as e:
        print(f"❌ Failed to open serial port {port}: {e}", file=sys.stderr)
        sys.exit(1)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(10)

    try:
        while True:
            client, _ = server.accept()
            try:
                raw_data = client.recv(1024).decode("utf-8", errors="ignore").strip()
                if not raw_data:
                    client.close()
                    continue

                session_id = "default"
                cmd = "G"

                # Check if payload is JSON query or update
                if raw_data.startswith("{") and raw_data.endswith("}"):
                    try:
                        payload = json.loads(raw_data)
                        if payload.get("action") == "status":
                            # Return detailed session list
                            resp_data = {
                                "status": "ok",
                                "aggregate": current_hardware_state,
                                "active_sessions": {
                                    sid: s["state"] for sid, s in active_sessions.items()
                                }
                            }
                            client.sendall(json.dumps(resp_data).encode("utf-8") + b"\n")
                            client.close()
                            continue

                        session_id = payload.get("session_id", "default")
                        cmd = payload.get("state", "G").upper()
                    except Exception:
                        cmd = raw_data.upper()
                else:
                    cmd = raw_data.upper()

                if cmd in ('RESET', 'CLEAR'):
                    active_sessions.clear()
                    new_state = 'G'
                elif cmd in ('R', 'B', 'Y', 'G', 'O', 'T'):
                    clean_stale_sessions()
                    if cmd == 'O':
                        if session_id in active_sessions:
                            del active_sessions[session_id]
                    else:
                        active_sessions[session_id] = {
                            "state": cmd,
                            "updated": time.time()
                        }
                    new_state = compute_aggregate_state() if cmd != 'T' else 'T'
                else:
                    new_state = current_hardware_state

                # Update physical hardware if aggregate changed
                if new_state != current_hardware_state or cmd == 'T':
                    ser.write(new_state.encode("utf-8"))
                    ser.flush()
                    current_hardware_state = new_state
                    summary = f"[{new_state}] (Active Sessions: {len(active_sessions)})"
                    print(f"🚦 Hardware updated ➔ {summary} | Triggered by session '{session_id[:12]}' -> {cmd}")

                client.sendall(json.dumps({
                    "status": "ok",
                    "aggregate": current_hardware_state,
                    "active_sessions": len(active_sessions)
                }).encode("utf-8") + b"\n")

            except Exception as e:
                print(f"Bridge request error: {e}", file=sys.stderr)
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
