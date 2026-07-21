
from typing import Dict, Any

class ApprovalWorkflow:
    def __init__(self):
        self.pending_approvals: Dict[str, Any] = {}
        
    def submit(self, task_id: str, payload: Any):
        self.pending_approvals[task_id] = {"status": "PENDING", "data": payload}
        
    def approve(self, task_id: str):
        if task_id in self.pending_approvals:
            self.pending_approvals[task_id]["status"] = "APPROVED"

