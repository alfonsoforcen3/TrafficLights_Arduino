#!/usr/bin/env python3
"""
traffic.py — Universal CLI Hook handler for Arduino Traffic Light.

Supports:
- G = Solid Green (Turn done / Standby)
- Y = Solid Yellow (Agent working / Thinking)
- R = Solid Red (Error / Blocked)
- B = Blinking Red (User Input / Permission Required)
- O = Off
- T = Test sequence
"""

import os
import sys
import glob
import json
import socket
import datetime
import serial

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765
BAUD_RATE = 115200
LOG_FILE = os.path.join(os.path.dirname(__file__), "traffic.log")
LATCH_FILE = "/tmp/traffic_error_latch"

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

def send_via_tcp(char_code):
    """Sends command to background bridge daemon if running."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.15)
        sock.connect((TCP_HOST, TCP_PORT))
        sock.sendall(char_code.encode("utf-8"))
        sock.recv(16)
        sock.close()
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False

def find_serial_port():
    override = os.environ.get("TRAFFIC_PORT")
    if override and os.path.exists(override):
        return override
    ports = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.usbmodem*")
    return ports[0] if ports else None

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

def resolve_color_code():
    arg = sys.argv[1].strip().upper() if len(sys.argv) > 1 else ""

    # Explicit reset command removes the latch
    if arg in ("RESET", "CLEAR"):
        if os.path.exists(LATCH_FILE):
            try:
                os.remove(LATCH_FILE)
            except Exception:
                pass
        return "G"

    # Explicit Red or Blinking Red command
    if arg in ("B", "BLINK", "INPUT", "ASK", "NOTIFICATION"):
        try:
            with open(LATCH_FILE, "w") as f:
                f.write("input_required_blinking")
        except Exception:
            pass
        return "B"

    if arg in ("R", "RED", "ERROR"):
        try:
            with open(LATCH_FILE, "w") as f:
                f.write("error_latched")
        except Exception:
            pass
        return "R"

    # If stdin JSON has an error, latch Red
    if not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read().strip()
            if stdin_data:
                parsed = json.loads(stdin_data)
                err = parsed.get("error")
                term = parsed.get("terminationReason")
                if err or term == "error":
                    try:
                        with open(LATCH_FILE, "w") as f:
                            f.write(str(err or term))
                    except Exception:
                        pass
                    return "R"
                event = parsed.get("hook_event_name") or parsed.get("event") or ""
                if event.upper() in EVENT_MAP:
                    return EVENT_MAP[event.upper()]
        except Exception:
            pass

    # If latch is active, hold latched state
    if os.path.exists(LATCH_FILE):
        try:
            with open(LATCH_FILE, "r") as f:
                content = f.read()
            if "blinking" in content or "input" in content:
                return "B"
        except Exception:
            pass
        return "R"

    if arg in EVENT_MAP:
        return EVENT_MAP[arg]

    return "G"

def main():
    color = resolve_color_code()

    success = send_via_tcp(color)
    channel = "bridge"

    if not success:
        success = send_via_direct_serial(color)
        channel = "direct_serial"

    log(f"Color: {color} | Success: {success} | Channel: {channel}")
    print("{}")
    sys.exit(0)

if __name__ == "__main__":
    main()
