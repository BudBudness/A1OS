import os
from generators.core.base_gen import BaseGenerator

class Generator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)
        self.name = "monitoring"
        self.dependencies = ["api"]

    def generate(self):
        artifacts = []
        core_src = """import os

class SovereignMonitoringTelemetry:
    def __init__(self):
        pass
    def capture_system_load(self):
        try:
            with open("/proc/loadavg", "r") as f:
                load = f.read().strip().split()
            return {"1m_load": float(load[0]), "5m_load": float(load[1]), "15m_load": float(load[2])}
        except:
            return {"1m_load": 0.00, "5m_load": 0.00, "15m_load": 0.00, "note": "procfs bounds unavailable"}
"""
        routes_src = """from api.router import SovereignAPIRouter
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
"""
        artifacts.append(self.emit_file("monitoring", "core.py", core_src))
        artifacts.append(self.emit_file("monitoring", "monitoring_routes.py", routes_src))
        return artifacts
