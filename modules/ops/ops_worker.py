import os
import psutil
from core.worker_base import BaseWorker

class OpsWorker(BaseWorker):
    def __init__(self):
        super().__init__("ops")

    def process_task(self, task):
        action = task.get("action", "diagnose")
        if action == "diagnose":
            process = psutil.Process(os.getpid())
            diagnostics = {
                "memory_rss_mb": process.memory_info().rss / (1024 * 1024),
                "cpu_percent": process.cpu_percent(interval=None),
                "status": "healthy",
                "storage_utilization": psutil.disk_usage('.').percent
            }
            self.save_state(diagnostics)
            return diagnostics
        return {"error": "Unknown operations action"}
