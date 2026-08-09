class MonitorEngine:
    def __init__(self):
        self.metrics = {}

    def log_event(self, event_type, data):
        self.metrics[event_type] = data

    def get_health_status(self):
        return {"status": "healthy", "metrics_count": len(self.metrics)}
