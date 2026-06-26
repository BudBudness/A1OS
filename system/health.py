from datetime import datetime

class HealthCheck:
    def check(self):
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}