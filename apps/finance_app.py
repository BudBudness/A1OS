import json
from workflow.engine import WorkflowEngine, Task

class FinanceApp:
    @staticmethod
    def run_compliance_check(task_id):
        task = WorkflowEngine.get_task(task_id)
        # Business Logic: Reject if budget exceeds threshold
        if task.required_budget > 100000:
            task.execution_log.append("COMPLIANCE_REJECT: Budget exceeds corporate limit.")
            task.status = "FAILED"
        else:
            task.execution_log.append("COMPLIANCE_PASS: Budget within corporate parameters.")
            task.status = "VERIFICATION"
        
        task.update_hash()
        WorkflowEngine._persist(task)
        return task.status
