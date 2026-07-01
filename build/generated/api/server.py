import sys
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
        print("\n[API-CORE] Safe teardown completed.")
        sys.exit(0)

if __name__ == "__main__":
    run_server()