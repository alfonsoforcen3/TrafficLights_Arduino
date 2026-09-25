#!/usr/bin/env python3
"""
bridge.py — Self-Healing Multi-Session Serial Bridge Daemon for Arduino Traffic Light.

Features:
- Self-Healing Hot-Plug: Auto-reconnects when the Arduino USB is unplugged/replugged or moves ports.
- Multi-Session Priority Resolution:
  1. 🚨 Blinking Red ('B'): If ANY session needs user input/permission
  2. 🔴 Solid Red ('R'):    If ANY session encountered an error
  3. 🟡 Solid Yellow ('Y'): If ANY session is currently working/thinking
  4. 🟢 Solid Green ('G'):  When ALL active sessions are finished/ready
  5. ⚫ Off ('O'):          When all sessions have ended
- Auto-Decay for Stale Sessions: Sessions stuck in 'Y' without activity for >3 minutes decay to 'G'.
- Status Query & Reset API over local TCP socket.
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
ser_conn = None

def find_serial_port():
    override = os.environ.get("TRAFFIC_PORT")
    if override:
        return override
    ports = list(serial.tools.list_ports.comports())
    # 1. Look for known Arduino/CH340/USB-serial chips
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "1a86:7523" in hwid or "ch340" in desc or "arduino" in desc or "usb" in desc or "serial" in desc:
            return p.device
    # 2. Look for COM/usb ports
    for p in ports:
        if p.device.upper().startswith("COM") or "usb" in p.device.lower():
            return p.device
    return ports[0].device if ports else None

def get_or_reconnect_serial():
    global ser_conn
    if ser_conn is not None and ser_conn.is_open:
        return ser_conn

    port = find_serial_port()
    if not port:
        return None

    try:
        print(f"🔌 (Re)connecting to Arduino on {port}...")
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(1.8) # Bootloader delay
        if ser.in_waiting:
            ser.read(ser.in_waiting)
        ser.write(current_hardware_state.encode("utf-8"))
        ser.flush()
        ser_conn = ser
        print(f"✅ Serial connected successfully on {port}!")
        return ser_conn
    except Exception as e:
        print(f"⚠️ Could not open {port}: {e}", file=sys.stderr)
        ser_conn = None
        return None

def write_to_hardware(state_char):
    global ser_conn, current_hardware_state
    ser = get_or_reconnect_serial()
    if not ser:
        current_hardware_state = state_char
        return False

    try:
        ser.write(state_char.encode("utf-8"))
        ser.flush()
        current_hardware_state = state_char
        return True
    except Exception as e:
        print(f"⚠️ Serial write failed ({e}). Attempting auto-reconnect...", file=sys.stderr)
        try:
            ser.close()
        except Exception:
            pass
        ser_conn = None
        # Try once to reconnect
        ser = get_or_reconnect_serial()
        if ser:
            try:
                ser.write(state_char.encode("utf-8"))
                ser.flush()
                current_hardware_state = state_char
                return True
            except Exception:
                pass
        return False

def compute_aggregate_state():
    """Calculates highest-priority state across all tracked sessions."""
    if not active_sessions:
        return 'G'

    states = [s["state"] for s in active_sessions.values()]

    if 'B' in states:
        return 'B'
    if 'R' in states:
        return 'R'
    if 'Y' in states:
        return 'Y'
    if 'G' in states:
        return 'G'

    return 'O'

def clean_stale_sessions():
    """
    Auto-decays stale sessions:
    - If a session is 'Y' (working) with no activity for >180s (3m), decay to 'G'.
    - If inactive for >600s (10m), drop from registry.
    """
    now = time.time()
    to_delete = []
    for sid, s in active_sessions.items():
        elapsed = now - s["updated"]
        if s["state"] == 'Y' and elapsed > 180:
            s["state"] = 'G'
            print(f"⏱️ Session '{sid[:12]}' decayed from Yellow to Green (idle for {int(elapsed)}s)")
        elif elapsed > 600:
            to_delete.append(sid)

    for sid in to_delete:
        del active_sessions[sid]

def run_bridge():
    global current_hardware_state
    print("=" * 60)
    print("🚦 ARDUINO TRAFFIC LIGHT — SELF-HEALING BRIDGE DAEMON")
    print("=" * 60)

    # Initial hardware connection attempt
    get_or_reconnect_serial()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(10)
    print(f"✅ Bridge server listening on {TCP_HOST}:{TCP_PORT}...\n")

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

                if raw_data.startswith("{") and raw_data.endswith("}"):
                    try:
                        payload = json.loads(raw_data)

                        # Status query
                        if payload.get("action") == "status":
                            clean_stale_sessions()
                            current_agg = compute_aggregate_state()
                            resp_data = {
                                "status": "ok",
                                "aggregate": current_agg,
                                "hardware_connected": ser_conn is not None and ser_conn.is_open,
                                "active_sessions": {
                                    sid: s["state"] for sid, s in active_sessions.items()
                                }
                            }
                            client.sendall(json.dumps(resp_data).encode("utf-8") + b"\n")
                            client.close()
                            continue

                        # Reset action
                        if payload.get("action") in ("reset", "clear"):
                            active_sessions.clear()
                            write_to_hardware('G')
                            client.sendall(b'{"status": "reset_ok"}\n')
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

                # Update physical hardware if state changed or test requested
                if new_state != current_hardware_state or cmd == 'T':
                    write_to_hardware(new_state)
                    summary = f"[{new_state}] (Active Sessions: {len(active_sessions)})"
                    print(f"🚦 Output ➔ {summary} | Triggered by '{session_id[:12]}' -> {cmd}")

                client.sendall(json.dumps({
                    "status": "ok",
                    "aggregate": current_hardware_state,
                    "active_sessions": len(active_sessions)
                }).encode("utf-8") + b"\n")

            except Exception as e:
                print(f"⚠️ Bridge request error: {e}", file=sys.stderr)
            finally:
                client.close()

    except KeyboardInterrupt:
        print("\nStopping bridge...")
    finally:
        try:
            if ser_conn and ser_conn.is_open:
                ser_conn.write(b'O')
                ser_conn.close()
            server.close()
        except Exception:
            pass

if __name__ == "__main__":
    run_bridge()
