import time

class SystemResourceMonitor:
    def __init__(self):
        self.metrics_store = []

    def poll_system_health(self):
        snapshot = {
            "timestamp": time.time(),
            "cpu_load_percent": 12.5,
            "memory_usage_mb": 256.0,
            "status": "nominal"
        }
        self.metrics_store.append(snapshot)
        print(f"[MONITOR-CORE] Polled health snapshot at {snapshot['timestamp']}")
        return snapshot