# workers/analytics.py
class AnalyticsWorker:
    def __call__(self, data):
        """Process analytics data"""
        return {
            "status": "success",
            "data": data,
            "worker": "analytics"
        }
