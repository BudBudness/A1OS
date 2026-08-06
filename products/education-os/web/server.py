from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

API = "http://127.0.0.1:3012"
WEB = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy(self.path[4:], "GET")
            return
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy(self.path[4:], "POST")

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self._proxy(self.path[4:], "PUT")

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            self._proxy(self.path[4:], "PATCH")

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._proxy(self.path[4:], "DELETE")

    def _proxy(self, suffix, method):
        target = API + "/" + suffix.lstrip("/")
        body = None
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            body = self.rfile.read(length)
        headers = {
            k: v
            for k, v in self.headers.items()
            if k.lower() not in ("host", "content-length", "accept-encoding", "connection")
        }
        try:
            req = Request(target, data=body, method=method, headers=headers)
            with urlopen(req, timeout=15) as r:
                data = r.read()
                self.send_response(r.status)
                self.send_header("Content-Type", r.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except HTTPError as e:
            try:
                data = e.read()
            except Exception:
                data = b""
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if data:
                self.wfile.write(data)
        except URLError as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        pass


ThreadingHTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
