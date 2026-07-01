from workflow.engine import WorkflowEngine
from apps.finance_app import FinanceApp

# 1. Create a task with a high budget to test rejection
tid_high = WorkflowEngine.create_task("CFO", "CEO", "FINANCE", 1, 150000.0)
status_high = FinanceApp.run_compliance_check(tid_high)

# 2. Create a task with a valid budget
tid_low = WorkflowEngine.create_task("CFO", "CEO", "FINANCE", 1, 50000.0)
status_low = FinanceApp.run_compliance_check(tid_low)

# 3. Verify
print(f"High Budget Task Status: {status_high}")
print(f"Low Budget Task Status: {status_low}")

task_low = WorkflowEngine.get_task(tid_low)
print(f"Low Budget Log: {task_low.execution_log[-1]}")
