from .logger import StructuredLogger
from .tracer import DiagnosticSpanTracer
from .formatter import DiagnosticLogFormatter
import time

def test_logging_subsystem():
    # 1. Verify structured logging emission
    logger = StructuredLogger("sys_init")
    entry = logger.log("info", "Boot sequence initiated", node_id="node_0")
    assert entry["level"] == "INFO"
    assert entry["message"] == "Boot sequence initiated"
    
    # 2. Verify span tracer latency tracking
    tracer = DiagnosticSpanTracer()
    span = tracer.start_span("disk_mount")
    time.sleep(0.01)
    tracer.end_span(span)
    assert span["status"] == "closed"
    assert span["duration_ms"] >= 0.0
    
    # 3. Verify serialization formatting
    formatted_json = DiagnosticLogFormatter.format_json(entry)
    assert "Boot sequence initiated" in formatted_json
    
    print("✅ Structured Event Logging & Diagnostic Tracing Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_logging_subsystem()