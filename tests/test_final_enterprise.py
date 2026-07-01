from executive.office.c_suite import CFO, CTO
from system.registry import SystemRegistry
from organization.departments.finance import FinanceDepartment
from organization.departments.engineering import EngineeringDepartment
from applications.trading_app import TradingApp

# Setup
FinanceDepartment()
EngineeringDepartment()
cfo = CFO("Alice")
cto = CTO("Bob")
cfo.add_handle("Finance", SystemRegistry.get_department_handle("Finance"))
cto.add_handle("Engineering", SystemRegistry.get_department_handle("Engineering"))

# App Setup with cross-authority
trading_desk = TradingApp("Global_Macro_Bot")
trading_desk.register_authority("Finance", cfo)
trading_desk.register_authority("Engineering", cto)

# Execution
print(trading_desk.run_strategy("Arbitrage_2026"))
