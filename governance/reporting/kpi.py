
from typing import Dict, Any

class KPIEngine:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}

    def update_okr(self, key: str, value: Any):
        self.metrics[key] = value

    def get_report(self) -> Dict[str, Any]:
        return self.metrics

