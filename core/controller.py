from workflow.engine import WorkflowEngine
from workflow.identity import IdentityManager
from apps.finance import RoyaltyEngine

class AgentController:
    def execute_as_agent(self, owner, target, app, priority, budget, secret):
        tid = WorkflowEngine.create_task(owner, target, app, priority, budget)
        sig = IdentityManager.sign_request(secret, tid)
        return {"task_id": tid, "signature": sig}
