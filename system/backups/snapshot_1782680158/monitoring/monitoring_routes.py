from api.router import SovereignAPIRouter
from monitoring.core import SovereignMonitoringTelemetry
import os
import gc

telemetry = SovereignMonitoringTelemetry()

@SovereignAPIRouter.register_route("/monitoring/metrics", method="GET")
def fetch_metrics(body):
    return 200, {
        "status": "HEALTHY",
        "pid": os.getpid(),
        "tracked_objects_gc": len(gc.get_objects()),
        "hardware_telemetry": telemetry.capture_system_load()
    }
