import os

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
