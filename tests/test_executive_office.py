from executive.ceo import CEO
from executive.office.c_suite import CFO
from core.registry import SystemRegistry
from organization.departments.finance import FinanceDepartment

# 1. Setup Org
FinanceDepartment() # Registers Finance
cfo = CFO("Alice")
cfo.add_handle("Finance", SystemRegistry.get_department_handle("Finance"))

# 2. Setup CEO
ceo = CEO("Eddie")
ceo.hire_executive("CFO", cfo)

# 3. Execution
print(ceo.command("CFO", "Finance", "Audit Q2 Expenses"))
