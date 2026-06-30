# control_plane/audit.py
import fcntl
from pathlib import Path

class AuditLogger:
    def __init__(self, log_path: str = "a1os_audit.log"):
        self.log_path = Path(log_path).expanduser()
        
    def log(self, event_type: str, details: str):
        with open(self.log_path, "a") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                f.write(f"[{event_type}] {details}\n")
            except BlockingIOError:
                pass # Drop log to avoid deadlocks on high concurrency
            finally:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass

audit = AuditLogger()
