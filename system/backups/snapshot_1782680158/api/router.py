import http.server
import json
import urllib.parse
import importlib
import os
import sys

class SovereignAPIRouter(http.server.BaseHTTPRequestHandler):
    routes = {}

    @classmethod
    def register_route(cls, path, method="GET"):
        def decorator(handler_func):
            if path not in cls.routes:
                cls.routes[path] = {}
            cls.routes[path][method.upper()] = handler_func
            print(f"[✔] Dynamic Endpoint Bound: {method.upper()} {path}")
            return handler_func
        return decorator

    @classmethod
    def automatic_module_discovery(cls, src_root):
        print("[*] API Gateway: Initiating automatic endpoint discovery loops...")
        for root_dir, _, files in os.walk(src_root):
            for file in files:
                if file.endswith("_routes.py") or (file.endswith(".py") and "endpoint" in file):
                    mod_name = file[:-3]
                    try:
                        if root_dir not in sys.path:
                            sys.path.insert(0, root_dir)
                        importlib.import_module(mod_name)
                    except Exception as e:
                        print(f"[✘] Failed to map configuration layout {file}: {str(e)}")

    def do_GET(self): self._dispatch("GET")
    def do_POST(self): self._dispatch("POST")

    def _dispatch(self, method):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path in self.routes and method in self.routes[path]:
            handler = self.routes[path][method]
            try:
                body = None
                if method == "POST":
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                status_code, response_data = handler(body)
                self._respond(status_code, response_data)
            except Exception as e:
                self._respond(500, {"status": "CRASHED", "error": str(e)})
        else:
            self._respond(404, {"status": "NOT_FOUND", "message": f"Route {method} {path} matches no active endpoints"})

    def _respond(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
