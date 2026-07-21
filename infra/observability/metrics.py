from prometheus_client import Counter, Histogram, start_http_server

EVENTS = Counter("a1os_events_total", "Total events processed")
LATENCY = Histogram("a1os_event_latency_seconds", "Event execution latency")

def record_event():
    EVENTS.inc()

def record_latency(fn):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = fn(*args, **kwargs)
        LATENCY.observe(time.time() - start)
        return result
    return wrapper

def start_metrics(port=9100):
    start_http_server(port)
