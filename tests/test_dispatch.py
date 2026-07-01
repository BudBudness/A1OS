from workflow.engine import WorkflowEngine
from workflow.dispatcher import WorkerRegistry, CapabilityDispatcher

# 1. Setup Environment
tid = WorkflowEngine.create_task("CFO", "CEO", "FINANCE", 1, 50000.0)
WorkerRegistry.register_worker("FINANCE", "ACCOUNTANT_01")

# 2. Advance to Assignment Stage
task = WorkflowEngine.get_task(tid)
task.status = "ASSIGN_WORKER"
task.checkpoint = "ASSIGN_WORKER"
WorkflowEngine._persist(task)

# 3. Dispatch
success = CapabilityDispatcher.dispatch(tid)

# 4. Verify
updated_task = WorkflowEngine.get_task(tid)
print(f"Dispatch Success: {success}")
print(f"Task Status: {updated_task.status}")
print(f"Log: {updated_task.execution_log[-1]}")
