import json
from http.server import BaseHTTPRequestHandler
from .middleware import apply_security_guards

class GeneratedRouter(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Mute verbose console logs to keep terminal tracking clear
        pass

    def _respond(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "healthy", "engine": "A1OS"})
        elif self.path == "/metrics":
            self._respond(200, {"cpu": "nominal", "sockets": "reusable"})
        else:
            self._respond(404, {"error": "endpoint_not_found"})

    def do_POST(self):
        # Extracted length configuration checks
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        
        # Injected Middleware Layer Checks
        passed, reason = apply_security_guards(self.headers, body)
        if not passed:
            self._respond(401, {"error": "unauthorized_boundary_access", "reason": reason})
            return

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "malformed_json"})
            return

        if self.path == "/telemetry":
            self._respond(202, {"status": "ingested", "keys": list(data.keys())})
        else:
            self._respond(404, {"error": "endpoint_not_mapped"})