"""Read-only, loopback-only customer dashboard; never expose chat/session content."""
import json
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

class Dashboard:
    def __init__(self, get_report, connected, root=None):
        self.get_report = get_report
        self.connected = connected
        self.root = Path(root or Path(__file__).resolve().parent.parent / 'web')
        self.history = deque(maxlen=120)
        self.last_sample = 0
        self.last_seen = 0

    def received(self, report):
        if report is None:
            self.history.clear()
            self.last_sample = self.last_seen = 0
        if report and report.get('battery'):
            now = time.time()
            self.last_seen = now
            if now - self.last_sample >= 55:
                b = report['battery']
                self.history.append({'time': now, 'sensor_voltage': b.get('sensor_voltage'),
                                     'voltage': b.get('voltage')})
                self.last_sample = now

    def status(self):
        report = self.get_report() or {}
        online = bool(self.connected())
        age = time.time() - self.last_seen if self.last_seen else None
        return {'connected': online, 'stale': not online or age is None or age > 90,
                'age_seconds': round(age) if age is not None else None,
                'battery': report.get('battery'), 'battery_error': report.get('battery_error'),
                'history': list(self.history), 'charging_verified': False}

    def start(self, port=8766):
        dashboard = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_GET(self):
                # Reject DNS rebinding. No CORS; public sites cannot read local telemetry.
                if self.headers.get('Host') not in ('127.0.0.1:'+str(server.server_port), 'localhost:'+str(server.server_port)):
                    self.send_error(403); return
                path = urlsplit(self.path).path
                if path == '/api/battery':
                    payload = json.dumps(dashboard.status()).encode()
                    mime = 'application/json'
                elif path in ('/', '/index.html', '/style.css', '/app.js'):
                    file = dashboard.root / ('index.html' if path == '/' else path[1:])
                    try:
                        payload = file.read_bytes()
                    except OSError:
                        self.send_error(503, 'Dashboard assets unavailable'); return
                    mime = {'html':'text/html', 'css':'text/css', 'js':'text/javascript'}[file.suffix[1:]]
                else:
                    self.send_error(404); return
                self.send_response(200)
                self.send_header('Content-Type', mime+'; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers(); self.wfile.write(payload)
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server
