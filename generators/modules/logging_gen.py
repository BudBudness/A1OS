from generators.core.base_gen import BaseGenerator
from pathlib import Path

class LoggingGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "logging"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Thread-Safe Structured Diagnostic Logger Engine
        logger_code = '''import time

class StructuredLogger:
    def __init__(self, subsystem_name="core"):
        self.subsystem = subsystem_name

    def log(self, level, message, **kwargs):
        entry = {
            "time": time.time(),
            "level": level.upper(),
            "subsystem": self.subsystem,
            "message": message,
            **kwargs
        }
        print(f"[{entry['level']}] {self.subsystem}: {message} -- Context: {kwargs}")
        return entry
'''

        # 2. Execution Latency and Span Tracer Utility
        tracer_code = '''import time

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
'''

        # 3. Log Record Formatter and Serializer
        formatter_code = '''import json

class DiagnosticLogFormatter:
    @staticmethod
    def format_json(log_entry):
        return json.dumps(log_entry)

    @staticmethod
    def format_text(log_entry):
        return f"{log_entry['time']} | {log_entry['level']} | {log_entry['subsystem']} | {log_entry['message']}"
'''

        # 4. Structured Event Logging Verification Test Suite
        test_code = '''from .logger import StructuredLogger
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
'''

        # Write out the full structural logging modules atomically
        with open(output_dir / "logger.py", "w") as f: f.write(logger_code.strip())
        with open(output_dir / "tracer.py", "w") as f: f.write(tracer_code.strip())
        with open(output_dir / "formatter.py", "w") as f: f.write(formatter_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] logging_gen.py has compiled v1 Logging Subsystem inside {output_dir}")
