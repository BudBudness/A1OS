class MetricAlertEngine:
    def __init__(self, max_cpu_threshold=80.0):
        self.max_cpu = max_cpu_threshold

    def evaluate_snapshot(self, health_snapshot):
        if health_snapshot.get("cpu_load_percent", 0.0) > self.max_cpu:
            return True, "high_cpu_load_anomaly"
        return False, "nominal_operational_metrics"