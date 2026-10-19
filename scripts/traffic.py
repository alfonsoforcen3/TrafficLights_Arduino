#!/usr/bin/env python3
"""
traffic.py — Multi-Session CLI Hook handler for Arduino Traffic Light.

Extracts session context from stdin (conversationId / sessionId)
and communicates with the background bridge to maintain Priority Resolution across
all active sessions.
"""

import os
import argparse
import sys
import json
import socket
import io
import queue
import threading

TCP_HOST = "127.0.0.1"
TCP_PORT = 8765

EVENT_MAP = {
    # Working / Thinking
    "Y": "Y",
    "YELLOW": "Y",
    "BEFOREAGENT": "Y",
    "PREINVOCATION": "Y",
    "BEFOREMODEL": "Y",
    "USERPROMPTSUBMIT": "Y",
    "BEFORETOOL": "Y",
    "AFTERTOOL": "Y",
    "PRETOOLUSE": "Y",
    "POSTTOOLUSE": "Y",
    "POSTTOOLUSEFAILURE": "Y",

    # Blinking Red / Input required
    "B": "B",
    "BLINK": "B",
    "BLINKING": "B",
    "INPUT": "B",
    "ASK": "B",
    "QUESTION": "B",
    "NOTIFICATION": "B",
    "PROMPT_USER": "B",
    "PERMISSIONREQUEST": "B",

    # Solid Red / Error
    "R": "R",
    "RED": "R",
    "BLOCKED": "R",
    "ERROR": "R",
    "STOPFAILURE": "R",

    # Green / Standby / Done
    "G": "G",
    "GREEN": "G",
    "AFTERAGENT": "G",
    "POSTINVOCATION": "G",
    "STOP": "G",
    "SESSIONSTART": "G",
    "READY": "G",
    "INTERRUPT": "G",

    # Off / Shutdown
    "O": "O",
    "OFF": "O",
    "SESSIONEND": "O",
    "EXIT": "O",

    # Test
    "T": "T",
    "TEST": "T"
}

def log(_message):
    """Compatibility no-op: observers never write prompts/session IDs or block on disk."""
    pass


def read_payload(stream=None, timeout=0.2, max_bytes=1024 * 1024):
    """Read one bounded JSON payload without waiting forever for pipe EOF.

    Raw descriptor reads avoid leaving a Python buffered-stdin lock held by a
    daemon reader at interpreter shutdown. No hardware or file I/O is attempted.
    """
    stream = sys.stdin if stream is None else stream
    try:
        if stream.isatty():
            return {}
    except (AttributeError, OSError):
        return {}
    if isinstance(stream, io.StringIO):
        raw = stream.read(max_bytes + 1)
        if len(raw.encode('utf-8')) > max_bytes:
            return {}
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else {}
        except (ValueError, TypeError):
            return {}
    try:
        descriptor = stream.fileno()
    except (AttributeError, OSError, ValueError):
        return {}
    result = queue.Queue(maxsize=1)
    def reader():
        raw = bytearray()
        try:
            while len(raw) <= max_bytes:
                chunk = os.read(descriptor, min(65536, max_bytes + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
                if len(raw) > max_bytes:
                    break
                try:
                    value = json.loads(raw)
                    result.put_nowait(value if isinstance(value, dict) else {})
                    return
                except (ValueError, UnicodeError):
                    pass
            result.put_nowait({})
        except (OSError, ValueError, queue.Full):
            try:
                result.put_nowait({})
            except queue.Full:
                pass
    threading.Thread(target=reader, daemon=True).start()
    try:
        return result.get(timeout=timeout)
    except queue.Empty:
        return {}


def send_via_tcp(session_id, char_code):
    """Best-effort loopback delivery; absent hardware never triggers USB probing."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.15)
            sock.connect((TCP_HOST, TCP_PORT))
            payload = json.dumps({'session_id': str(session_id)[:128], 'state': char_code}, ensure_ascii=False)
            sock.sendall(payload.encode('utf-8'))
            # The observer does not require an acknowledgement. The bridge is
            # responsible for Bluetooth/serial and delivery diagnostics.
            return True, None
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False, None


def options():
    parser = argparse.ArgumentParser(description='Send a provider/session lifecycle signal to the traffic light.')
    parser.add_argument('event', nargs='?', default='')
    parser.add_argument('--provider', default='codex', help='Provider namespace, e.g. codex, claude, custom')
    parser.add_argument('--session-id', help='Stable chat ID for integrations without JSON stdin')
    parser.add_argument('--trafficlights-hook', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--cursor-prompt', action='store_true', help='Cursor prompt observer response; never a tool approval')
    parser.add_argument('--silent', action='store_true', help='Emit no stdout context (Claude command hooks)')
    args = parser.parse_args()
    if not args.provider or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in args.provider):
        parser.error('provider must contain only lowercase letters, digits, underscores or hyphens')
    return args

def parse_input(args=None):
    args = options() if args is None else args
    arg = args.event.strip().upper()
    session_id = f"proc_{os.getppid()}"
    parsed_payload = {}

    parsed_payload = read_payload()
    session_id = (parsed_payload.get('conversationId') or parsed_payload.get('sessionId') or
                  parsed_payload.get('conversation_id') or parsed_payload.get('session_id') or session_id)

    session_id = args.provider + ':' + str(args.session_id or session_id)
    event = str(parsed_payload.get('hook_event_name') or parsed_payload.get('event') or '').upper()
    if args.provider == 'gemini' and event == 'NOTIFICATION':
        return session_id, 'B' if parsed_payload.get('notification_type') == 'ToolPermission' else None
    if args.provider == 'cursor':
        if event == 'STOP':
            return session_id, 'R' if parsed_payload.get('status') == 'error' else 'G'
        return session_id, {'BEFORESUBMITPROMPT':'Y','AFTERAGENTTHOUGHT':'Y',
                            'AFTERAGENTRESPONSE':'Y','SESSIONSTART':'G','SESSIONEND':'O'}.get(event, EVENT_MAP.get(arg, 'Y'))
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
        if args.provider == "claude" and parsed_payload.get("hook_event_name") == "PostToolUseFailure":
            return session_id, "Y"
        if err or term == "error":
            return session_id, "R"
        event = str(parsed_payload.get("hook_event_name") or parsed_payload.get("event") or "")
        tool = str(parsed_payload.get('tool_name') or '')
        if event.upper() in ('PRETOOLUSE', 'POSTTOOLUSE', 'BEFORETOOL') and (
                'request_user_input' in tool or (tool == 'AskUserQuestion' and event.upper() == 'PRETOOLUSE') or
                (tool == 'ask_user' and event.upper() == 'BEFORETOOL')):
            return session_id, 'B'
        if event.upper() in EVENT_MAP:
            return session_id, EVENT_MAP[event.upper()]

    if arg in EVENT_MAP:
        return session_id, EVENT_MAP[arg]

    return session_id, "G"

def main():
    """Observe lifecycle only: always fail open, never approve/block/continue AI."""
    args = None
    try:
        args = options()
        session_id, color = parse_input(args)
        if color is not None:
            send_via_tcp(session_id, color)
    except (Exception, SystemExit):
        # Malformed input, argument drift, missing helper or network failure must
        # not become a provider decision or an agent-blocking nonzero exit.
        pass
    if args is not None and args.silent:
        raise SystemExit(0)
    try:
        # Cursor beforeSubmitPrompt explicitly requires a pass-through response;
        # all other observers return the empty JSON object (including Codex Stop).
        print(json.dumps({'continue': True}) if args is not None and args.cursor_prompt else '{}', flush=True)
    except (OSError, ValueError):
        # Avoid a second broken-pipe flush at interpreter shutdown (exit 120).
        sys.stdout = io.StringIO()
    raise SystemExit(0)


if __name__ == '__main__':
    raise SystemExit(main())
