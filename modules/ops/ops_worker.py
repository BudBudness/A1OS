import os
import shutil
from core.worker_base import BaseWorker

class OpsWorker(BaseWorker):
    def __init__(self):
        super().__init__("ops")

    def process_task(self, task):
        action = task.get("action", "diagnose")
        if action == "diagnose":
            # Read PID status for RSS memory
            memory_rss_mb = 0.0
            try:
                with open(f"/proc/{os.getpid()}/statm", "r") as f:
                    # statm fields: size resident shared text lib data dirty
                    resident_pages = int(f.read().split()[1])
                    memory_rss_mb = (resident_pages * os.sysconf("SC_PAGE_SIZE")) / (1024 * 1024)
            except Exception:
                memory_rss_mb = -1.0

            # Calculate disk usage using shutil (Python Standard Library)
            disk_util = 0.0
            try:
                total, used, free = shutil.disk_usage(".")
                disk_util = (used / total) * 100
            except Exception:
                disk_util = -1.0

            diagnostics = {
                "memory_rss_mb": round(memory_rss_mb, 2),
                "cpu_percent": 0.0, # Placeholder without low-level C bindings
                "status": "healthy",
                "storage_utilization": round(disk_util, 2)
            }
            self.save_state(diagnostics)
            return diagnostics
        return {"error": "Unknown operations action"}
