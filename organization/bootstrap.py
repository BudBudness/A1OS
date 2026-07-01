from organization.departments.finance import FinanceDepartment
from organization.departments.engineering import EngineeringDepartment
from system.registry import SystemRegistry

def initialize_org():
    FinanceDepartment() # Registers itself via BaseDepartment
    EngineeringDepartment() # Registers itself via BaseDepartment
    return True
