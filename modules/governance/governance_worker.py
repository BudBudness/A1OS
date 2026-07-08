import json
from core.worker_base import BaseWorker

class GovernanceWorker(BaseWorker):
    def __init__(self):
        super().__init__("governance")
        self.kernel = None

    def process_task(self, task):
        # Admin task routing
        action = task.get("action", "audit")
        state = self.load_state()
        
        if action == "update_policy":
            policy = task.get("policy", {})
            with open("cfg/policies.json", 'w') as f:
                json.dump(policy, f)
            return {"status": "Policy updated successfully"}
            
        return {"status": "Audit complete", "logs": state.get("logs", [])}

    def load_policy(self):
        try:
            with open("cfg/policies.json", 'r') as f: return json.load(f)
        except: return {"min_length": 15, "restricted": ["restricted"]}

    def validate(self, output):
        policy = self.load_policy()
        if len(output) < policy.get("min_length", 0): return False, "Length violation"
        if any(w in output.lower() for w in policy.get("restricted", [])): return False, "Restricted content"
        return True, "Valid"

    def remediate(self, task):
        task["data"] = f"{task.get('data')} [Remediated]"
        return task

    def log_event(self, event_data):
        state = self.load_state()
        state.setdefault("logs", []).append(event_data)
        self.save_state(state)
