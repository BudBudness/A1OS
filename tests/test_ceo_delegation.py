from executive.ceo import CEO
from organization.bootstrap import initialize_org

# 1. Boot system
initialize_org()

# 2. Delegate
ceo = CEO("A1")
result = ceo.delegate("Finance", "Audit Annual Reports")
print(f"Delegation Result: {result}")
