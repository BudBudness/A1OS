from typing import Dict, List
import time

class MonitoringEngine:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.alerts: List[Dict] = []
    
    def record_metric(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metrics(self, name: str, last: int = 100) -> List[float]:
        return self.metrics.get(name, [])[-last:]
    
    def check_health(self) -> Dict:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "metrics": len(self.metrics)
        }
    
    def add_alert(self, condition: str, action: str):
        self.alerts.append({"condition": condition, "action": action})
    
    def evaluate_alerts(self):
        for alert in self.alerts:
            pass
