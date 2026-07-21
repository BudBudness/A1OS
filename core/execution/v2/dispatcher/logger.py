import os
import json

class LoggingGate:
    def __init__(self, log_path="~/A1OS/logs/pending_decisions.log"):
        self.log_path = os.path.expanduser(log_path)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_for_review(self, task_id, decision):
        with open(self.log_path, "a") as f:
            entry = {"task_id": task_id, "decision": decision}
            f.write(json.dumps(entry) + "\n")
        print(f"[PRE-REVIEW] Decision logged: {task_id}")
