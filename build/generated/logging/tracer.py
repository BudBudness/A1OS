import time

class DiagnosticSpanTracer:
    def __init__(self):
        self.active_spans = []

    def start_span(self, operation_name):
        span = {"op": operation_name, "start_time": time.time(), "status": "active"}
        self.active_spans.append(span)
        return span

    def end_span(self, span):
        span["duration_ms"] = (time.time() - span["start_time"]) * 1000.0
        span["status"] = "closed"
        print(f"[TRACER] Span closed: {span['op']} took {span['duration_ms']:.2f}ms")
        return span