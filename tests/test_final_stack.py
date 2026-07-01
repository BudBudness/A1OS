from core.bus import EventBus
from workflow.rbac import RBAC
from dashboard import Dashboard
from workflow.engine import WorkflowEngine

# Test Event Bus
def notify(data): print(f"Event Received: {data}")
EventBus.subscribe("TASK_COMPLETED", notify)
EventBus.publish("TASK_COMPLETED", "Task #123")

# Test RBAC
tid = WorkflowEngine.create_task("CEO", "CFO", "FINANCE", 1, 100.0)
authorized = RBAC.authorize("CEO", tid, "EXECUTE")
print(f"User Authorized: {authorized}")

# Test Dashboard
count, sizes = Dashboard.get_system_metrics()
print(f"System Load: {count} tasks tracked.")
