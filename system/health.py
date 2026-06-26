import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

class HealthCheck:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path

    def check(self) -> Dict[str, Any]:
        status = {"status": "healthy", "timestamp": datetime.now().isoformat(), "checks": {}}
        # Check database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            status["checks"]["database"] = "ok"
        except Exception as e:
            status["checks"]["database"] = f"error: {str(e)}"
            status["status"] = "degraded"
        return status
