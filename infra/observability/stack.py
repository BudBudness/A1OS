from prometheus_client import start_http_server, Counter

REQUESTS = Counter("a1os_requests_total", "Total requests")

def start_metrics(port=9100):
    start_http_server(port)

def record_request():
    REQUESTS.inc()
