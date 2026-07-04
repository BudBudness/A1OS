
import time
from typing import Dict

class MetricsCollector:
    def __init__(self):
        self.data: Dict[str, float] = {}
        
    def record(self, metric_name: str, value: float):
        self.data[metric_name] = value

class Logger:
    def log(self, level: str, message: str):
        print(f"[{time.strftime("%Y-%m-%d %H:%M:%S")}] {level}: {message}")

