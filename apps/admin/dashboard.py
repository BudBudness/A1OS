from typing import Dict, List
import psutil
import time

class AdminDashboard:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    def get_system_metrics(self) -> Dict:
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict()
        }
    
    def get_app_metrics(self) -> Dict:
        return {
            "status": "online",
            "uptime": time.time(),
            "version": "1.0.0"
        }
    
    def get_logs(self, lines: int = 100) -> List[str]:
        return ["[INFO] System online", "[INFO] No errors"]
