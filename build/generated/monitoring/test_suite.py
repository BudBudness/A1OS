from .monitor import SystemResourceMonitor
from .metric_store import InMemoryMetricStore
from .alert import MetricAlertEngine

def test_monitoring_subsystem():
    monitor = SystemResourceMonitor()
    store = InMemoryMetricStore()
    alert_engine = MetricAlertEngine(max_cpu_threshold=50.0)
    
    # 1. Poll system health snapshot assertion
    snapshot = monitor.poll_system_health()
    assert snapshot is not None
    assert snapshot["status"] == "nominal"
    
    # 2. Append in-memory telemetry metric assertion
    store.append_metric("network_latency_ms", 14.2)
    metrics = store.get_metrics_by_name("network_latency_ms")
    assert len(metrics) == 1
    assert metrics[0]["value"] == 14.2
    
    # 3. Verify threshold anomaly triggering logic
    is_alert, reason = alert_engine.evaluate_snapshot({
        "cpu_load_percent": 85.0
    })
    assert is_alert is True
    assert reason == "high_cpu_load_anomaly"
    
    print("✅ Telemetry System Monitoring Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_monitoring_subsystem()