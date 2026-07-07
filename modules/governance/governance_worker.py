import json
from core.worker_base import BaseWorker

class GovernanceWorker(BaseWorker):
    def __init__(self):
        super().__init__("governance")

    def validate(self, output):
        # output is now a dict
        content = output.get("content", "")
        confidence = output.get("confidence", 0)
        
        if confidence < 0.8: return False, "Low confidence"
        if "restricted" in content.lower(): return False, "Restricted"
        return True, "Valid"

    def remediate(self, task):
        task["data"] = f"{task.get('data')} [Remediated]"
        return task
