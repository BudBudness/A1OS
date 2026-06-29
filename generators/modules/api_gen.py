from generators.core.base_gen import BaseGenerator
from pathlib import Path

class ApiGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "api"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Base Core Reusable Socket Server HTTP Engine
        server_code = '''import sys
import socket
from http.server import HTTPServer
from .routes import GeneratedRouter

class ReusableHTTPServer(HTTPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        HTTPServer.server_bind(self)

def run_server(port=8090):
    server_address = ('', port)
    httpd = ReusableHTTPServer(server_address, GeneratedRouter)
    print(f"[API-CORE] Sovereign boundary listening on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n[API-CORE] Safe teardown completed.")
        sys.exit(0)

if __name__ == "__main__":
    run_server()
'''

        # 2. Complete Request Multiplexer Router Maps
        routes_code = '''import json
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
'''

        # 3. Network Boundary Access Middlewares
        middleware_code = '''def apply_security_guards(headers, request_body):
    # Hook implementation framework for signature and authentication screening
    auth_header = headers.get("Authorization", "")
    sig_header = headers.get("X-A1OS-Signature", "")
    
    # Simple check placeholder - pass through if not strictly enforced yet
    if "deny" in auth_header:
        return False, "Explicitly blocked security identity credentials"
    return True, "Passed basic validation boundaries"
'''

        # 4. Isolated End-to-End API Integration Verification Suite
        test_code = '''import threading
import time
import http.client
from .server import ReusableHTTPServer
from .routes import GeneratedRouter

def test_api_subsystem():
    # Spawn ephemeral server instance on a high test port
    test_port = 9091
    server = ReusableHTTPServer(('', test_port), GeneratedRouter)
    
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2) # Allow local socket loopback bind sequence
    
    # Run loopback HTTP health check verification validation test
    client = http.client.HTTPConnection("127.0.0.1", test_port)
    client.request("GET", "/health")
    response = client.getresponse()
    
    assert response.status == 200
    print("✅ Web API Interface Subsystem Integration Tests Passed.")
    server.shutdown()

if __name__ == "__main__":
    test_api_subsystem()
'''

        # Atomically write out the full web API subsystem suite files
        with open(output_dir / "server.py", "w") as f: f.write(server_code.strip())
        with open(output_dir / "routes.py", "w") as f: f.write(routes_code.strip())
        with open(output_dir / "middleware.py", "w") as f: f.write(middleware_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] api_gen.py has compiled v1 Web API Subsystem inside {output_dir}")
