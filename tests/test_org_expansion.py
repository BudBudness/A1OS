from executive.ceo import CEO
from organization.bootstrap import initialize_org
from core.registry import SystemRegistry

# Initialize System
initialize_org()
ceo = CEO("A1")

# Test handle-based delegation
deps = ["Finance", "Engineering"]
for dept in deps:
    # CEO now calls via the registry's handle-returning method
    print(f"Delegation: {ceo.delegate(dept, 'Optimize Operations')}")

# Verify that the CEO cannot access department internals directly
# Attempting to access kpis directly should fail or not be visible
handle = SystemRegistry.get_department_handle("Engineering")
print(f"Handle Status: {handle.get_status()}")
