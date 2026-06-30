import socketserver
import os
from api.router import SovereignAPIRouter

class SovereignAPIGateway:
    def __init__(self, port=8030):
        self.port = port

    def start(self):
        socketserver.TCPServer.allow_reuse_address = True
        base_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        SovereignAPIRouter.automatic_module_discovery(base_src)
        print(f"[*] API Gateway bound. Spinning core single-process matrix on port {self.port}...")
        with socketserver.TCPServer(("", self.port), SovereignAPIRouter) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] API Gateway shifting runlevel down gracefully.")
