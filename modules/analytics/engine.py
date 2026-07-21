import sqlite3
class AnalyticsEngine:
    def __init__(self, db="a1os_state.db"): self.db = db
    async def aggregate_metrics(self, d: dict) -> dict:
        v = float(d.get("memory_free_mb", 0.0))
        with sqlite3.connect(self.db, timeout=10.0) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO analytics_snapshots (metric_key, metric_value) VALUES (?,?) ON CONFLICT(metric_key) DO UPDATE SET metric_value=excluded.metric_value, last_calculated=CURRENT_TIMESTAMP", ("last_memory_free_mb", v))
            conn.commit()
        return {"aggregated_metric": "last_memory_free_mb", "value": v}
