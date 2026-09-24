#!/usr/bin/env python3
"""
traffic.py — Multi-Session CLI Hook handler for Arduino Traffic Light.

Extracts session context from stdin (conversationId / sessionId)
and communicates with the background bridge to maintain Priority Resolution across
all active sessions.
"""

import os
import sys
import glob
import json
import socket
import datetime
import serial
import serial.tools.list_ports

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765
BAUD_RATE = 115200
LOG_FILE = os.path.join(os.path.dirname(__file__), "traffic.log")

EVENT_MAP = {
    # Working / Thinking
    "Y": "Y",
    "YELLOW": "Y",
    "BEFOREAGENT": "Y",
    "PREINVOCATION": "Y",
    "BEFOREMODEL": "Y",
    "USERPROMPTSUBMIT": "Y",
    "BEFORETOOL": "Y",

    # Blinking Red / Input required
    "B": "B",
    "BLINK": "B",
    "BLINKING": "B",
    "INPUT": "B",
    "ASK": "B",
    "QUESTION": "B",
    "NOTIFICATION": "B",
    "PROMPT_USER": "B",

    # Solid Red / Error
    "R": "R",
    "RED": "R",
    "BLOCKED": "R",
    "ERROR": "R",

    # Green / Standby / Done
    "G": "G",
    "GREEN": "G",
    "AFTERAGENT": "G",
    "POSTINVOCATION": "G",
    "STOP": "G",
    "SESSIONSTART": "G",
    "READY": "G",

    # Off / Shutdown
    "O": "O",
    "OFF": "O",
    "SESSIONEND": "O",
    "EXIT": "O",

    # Test
    "T": "T",
    "TEST": "T"
}

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

def send_via_tcp(session_id, char_code):
    """Sends session-aware state update to background bridge."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        sock.connect((TCP_HOST, TCP_PORT))
        payload = json.dumps({
            "session_id": str(session_id),
            "state": char_code
        })
        sock.sendall(payload.encode("utf-8"))
        resp = sock.recv(1024).decode("utf-8", errors="ignore")
        sock.close()
        return True, resp.strip()
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False, None

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

def send_via_direct_serial(char_code):
    """Direct serial fallback when bridge is not running."""
    port = find_serial_port()
    if not port:
        log("No serial port found.")
        return False
    try:
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = BAUD_RATE
        ser.timeout = 0.5
        ser.dtr = False
        ser.open()
        ser.write(char_code.encode("utf-8"))
        ser.flush()
        ser.close()
        return True
    except Exception as e:
        log(f"Direct serial write error: {e}")
        return False

def parse_input():
    arg = sys.argv[1].strip().upper() if len(sys.argv) > 1 else ""
    session_id = f"proc_{os.getppid()}"
    parsed_payload = {}

    # Inspect stdin for session ID and error status
    if not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read().strip()
            if stdin_data:
                parsed_payload = json.loads(stdin_data)
                session_id = parsed_payload.get("conversationId") or \
                             parsed_payload.get("sessionId") or \
                             parsed_payload.get("session_id") or session_id
        except Exception:
            pass

    # Determine command/color
    if arg in ("RESET", "CLEAR"):
        return session_id, "RESET"

    # Input required trigger
    if arg in ("B", "BLINK", "INPUT", "ASK", "NOTIFICATION"):
        return session_id, "B"

    # Error trigger
    if arg in ("R", "RED", "ERROR"):
        return session_id, "R"

    # Check stdin payload for error / termination conditions
    if parsed_payload:
        err = parsed_payload.get("error")
        term = parsed_payload.get("terminationReason")
        if err or term == "error":
            return session_id, "R"
        event = parsed_payload.get("hook_event_name") or parsed_payload.get("event") or ""
        if event.upper() in EVENT_MAP:
            return session_id, EVENT_MAP[event.upper()]

    if arg in EVENT_MAP:
        return session_id, EVENT_MAP[arg]

    return session_id, "G"

def main():
    session_id, color = parse_input()

    success, resp = send_via_tcp(session_id, color)
    channel = "bridge"

    if not success:
        success = send_via_direct_serial(color)
        channel = "direct_serial"

    log(f"Session: {session_id[:12]} | State: {color} | Success: {success} | Channel: {channel} | Resp: {resp}")
    print("{}")
    sys.exit(0)

if __name__ == "__main__":
    main()
