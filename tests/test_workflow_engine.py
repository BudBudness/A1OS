from executive.ceo import CEO
from executive.office.c_suite import CFO
from system.registry import SystemRegistry
from organization.departments.finance import FinanceDepartment
from workflow.engine import WorkflowEngine

# Setup
FinanceDepartment()
cfo = CFO("Alice")
cfo.add_handle("Finance", SystemRegistry.get_department_handle("Finance"))
ceo = CEO("Eddie")
ceo.hire_executive("CFO", cfo)

# Execute
result = ceo.command("CFO", "Finance", "Process Annual Payroll")
print(result)

# Inspect Workflow Engine State
# We can find the task by looking at the registry
last_task_id = list(WorkflowEngine._registry.keys())[0]
print(f"Workflow State: {WorkflowEngine.get_task(last_task_id)['status']}")
