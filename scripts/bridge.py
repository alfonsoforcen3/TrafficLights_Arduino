#!/usr/bin/env python3
"""
bridge.py — True Plug & Go Multi-Session Serial Bridge Daemon for Arduino Traffic Light.

Features:
- Background Hardware Watchdog: Continuously monitors USB connection.
  When you plug in the Arduino, it automatically connects and immediately illuminates
  the correct LED within 2 seconds. No manual restart needed!
- True Plug & Go: Handles unplugs, replugs, and moving across USB ports seamlessly.
- Thread-Safe Communication: Decouples USB serial management from TCP hook requests.
- Multi-Session Priority Resolution:
  1. 🚨 Blinking Red ('B'): If ANY session needs user input/permission
  2. 🔴 Solid Red ('R'):    If ANY session encountered an error
  3. 🟡 Solid Yellow ('Y'): If ANY session is currently working/thinking
  4. 🟢 Solid Green ('G'):  When ALL active sessions are finished/ready
  5. ⚫ Off ('O'):          When all sessions have ended
- Auto-Decay for Stale Sessions: Sessions stuck in 'Y' for >3m decay to 'G'.
"""

import os
import sys
import json
import time
import socket
import threading
import serial
import serial.tools.list_ports

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765
BAUD_RATE = 115200

# Registry & Hardware state
active_sessions = {}
current_hardware_state = 'G'
hardware_synced = False
ser_conn = None
ser_lock = threading.Lock()

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
    # 2. Look for COM ports on Windows or USB ports on Mac/Linux
    for p in ports:
        if p.device.upper().startswith("COM") or "usb" in p.device.lower():
            return p.device
    return ports[0].device if ports else None

def hardware_watchdog():
    """
    Background worker that watches for the Arduino USB connection:
    - Auto-detects whenever you plug the Arduino into any port.
    - Waits for bootloader (1.8s) and immediately writes current state.
    - Detects disconnects and cleans up automatically.
    """
    global ser_conn, hardware_synced
    print("👀 Hardware Watchdog started. Monitoring for Arduino USB connection...", flush=True)

    while True:
        with ser_lock:
            # 1. If currently connected, check if port is still alive
            if ser_conn is not None:
                port_alive = False
                try:
                    if os.name == 'nt':
                        # Windows port existence check
                        port_alive = any(p.device.upper() == ser_conn.port.upper() for p in serial.tools.list_ports.comports())
                    else:
                        # POSIX file path existence check
                        port_alive = os.path.exists(ser_conn.port)
                except Exception:
                    port_alive = False

                if not port_alive:
                    print(f"⚠️ Arduino was unplugged from {ser_conn.port}.", flush=True)
                    try:
                        ser_conn.close()
                    except Exception:
                        pass
                    ser_conn = None
                    hardware_synced = False

            # 2. If not connected, scan and connect
            if ser_conn is None:
                port = find_serial_port()
                if port:
                    print(f"🔌 Detected Arduino on {port}! Connecting...", flush=True)
                    try:
                        ser = serial.Serial(port, BAUD_RATE, timeout=1)
                        # Bootloader delay
                        time.sleep(1.8)
                        if ser.in_waiting:
                            ser.read(ser.in_waiting)
                        # Immediately sync current state
                        ser.write(current_hardware_state.encode("utf-8"))
                        ser.flush()
                        ser_conn = ser
                        hardware_synced = True
                        print(f"✅ Plug & Go Ready: Connected to {port} and synced state [{current_hardware_state}]!", flush=True)
                    except Exception as e:
                        # Port might still be enumerating by OS
                        ser_conn = None
                        hardware_synced = False

        time.sleep(1.0)

def write_to_hardware(state_char):
    """Sends a state character to the Arduino (thread-safe)."""
    global current_hardware_state, hardware_synced
    current_hardware_state = state_char

    with ser_lock:
        if ser_conn is not None and ser_conn.is_open:
            try:
                ser_conn.write(state_char.encode("utf-8"))
                ser_conn.flush()
                hardware_synced = True
                return True
            except Exception as e:
                print(f"⚠️ Serial write failed ({e}). Watchdog will reconnect.", flush=True)
                try:
                    ser_conn.close()
                except Exception:
                    pass
                ser_conn = None
                hardware_synced = False
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
    """Auto-decays stale sessions: >180s without update decays to 'G'."""
    now = time.time()
    to_delete = []
    for sid, s in active_sessions.items():
        elapsed = now - s["updated"]
        if s["state"] == 'Y' and elapsed > 180:
            s["state"] = 'G'
            print(f"⏱️ Session '{sid[:12]}' decayed from Yellow to Green (idle for {int(elapsed)}s)", flush=True)
        elif elapsed > 600:
            to_delete.append(sid)

    for sid in to_delete:
        del active_sessions[sid]

def is_hardware_connected():
    with ser_lock:
        return ser_conn is not None and ser_conn.is_open

def get_active_port():
    with ser_lock:
        return ser_conn.port if (ser_conn is not None and ser_conn.is_open) else None

def run_bridge():
    global current_hardware_state, ser_conn, hardware_synced
    print("=" * 60)
    print("🚦 ARDUINO TRAFFIC LIGHT — TRUE PLUG & GO BRIDGE DAEMON")
    print("=" * 60)

    # Start the hardware watchdog thread
    watchdog_thread = threading.Thread(target=hardware_watchdog, daemon=True)
    watchdog_thread.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(10)
    print(f"✅ Bridge TCP server listening on {TCP_HOST}:{TCP_PORT}...\n", flush=True)

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
                                "hardware_connected": is_hardware_connected(),
                                "port": get_active_port(),
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

                # Update physical hardware if state changed, test requested, or not synced
                if new_state != current_hardware_state or cmd == 'T' or not hardware_synced:
                    write_to_hardware(new_state)
                    summary = f"[{new_state}] (Active Sessions: {len(active_sessions)})"
                    print(f"🚦 Hardware ➔ {summary} | Triggered by '{session_id[:12]}' -> {cmd}", flush=True)

                client.sendall(json.dumps({
                    "status": "ok",
                    "aggregate": current_hardware_state,
                    "hardware_connected": is_hardware_connected(),
                    "active_sessions": len(active_sessions)
                }).encode("utf-8") + b"\n")

            except Exception as e:
                print(f"⚠️ Bridge request error: {e}", file=sys.stderr, flush=True)
            finally:
                client.close()

    except KeyboardInterrupt:
        print("\nStopping bridge...", flush=True)
    finally:
        try:
            with ser_lock:
                if ser_conn and ser_conn.is_open:
                    ser_conn.write(b'O')
                    ser_conn.close()
            server.close()
        except Exception:
            pass

if __name__ == "__main__":
    run_bridge()
