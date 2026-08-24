import json
import time
from pathlib import Path


class AuditTrail:
    def __init__(self, path="deploy/audit_trail.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event_type, details=None):
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details or {},
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry
