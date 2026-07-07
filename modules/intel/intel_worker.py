from core.worker_base import BaseWorker

class IntelWorker(BaseWorker):
    def __init__(self):
        super().__init__("intel")

    def process_task(self, task):
        # Intel gathering simulation
        data = task.get("data", "")
        # Add metadata for governance validation
        report = {
            "query": data,
            "content": f"Detailed report on {data}...",
            "confidence": 0.95,
            "status": "raw"
        }
        
        # Remediation: If flagged, the governance layer updates the task
        if "[Remediated]" in data:
            report["status"] = "verified"
            report["content"] += " [Validated Source]"

        self.save_state(report)
        return report
