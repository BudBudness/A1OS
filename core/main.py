import json
import sys
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from routes.webhooks import handle_whatsapp_request
from routes.payments import handle_pesapal_payment
from routes.ingest import handle_intelligence_ingest

class A1OSCoreRouter(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stdout.write(f"[ROUTER-LOG] {format%args}\n")

    def do_GET(self):
        if self.path == "/api/v1/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif self.path == "/api/v1/routes":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            routes = {
                "GET": ["/api/v1/health", "/api/v1/routes"],
                "POST": ["/api/v1/webhooks/whatsapp", "/api/v1/payments/pesapal", "/api/v1/ingest/trigger"]
            }
            self.wfile.write(json.dumps(routes).encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/v1/webhooks/whatsapp"):
            handle_whatsapp_request(self)
        elif self.path.startswith("/api/v1/payments/pesapal"):
            handle_pesapal_payment(self)
        elif self.path.startswith("/api/v1/ingest/trigger"):
            handle_intelligence_ingest(self)
        else:
            self.send_error(404)

class ReusableHTTPServer(HTTPServer):
    def server_bind(self):
        # Force low-level socket options to completely bypass Address Already In Use
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass # Fallback if SO_REUSEPORT isn't supported on this specific kernel build
        HTTPServer.server_bind(self)

if __name__ == "__main__":
    server_address = ('', 8086)
    try:
        httpd = ReusableHTTPServer(server_address, A1OSCoreRouter)
        print("A1OS Unified Authoritative Server online on port 8086...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server safely.")
        sys.exit(0)
