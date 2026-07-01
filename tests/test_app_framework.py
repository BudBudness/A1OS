from executive.ceo import CEO
from executive.office.c_suite import CFO, CTO
from core.registry import SystemRegistry
from organization.departments.finance import FinanceDepartment
from organization.departments.engineering import EngineeringDepartment
from applications.trading_app import TradingApp

# 1. Setup Infrastructure
FinanceDepartment()
EngineeringDepartment()
cfo = CFO("Alice")
cto = CTO("Bob")
cfo.add_handle("Finance", SystemRegistry.get_department_handle("Finance"))
cto.add_handle("Engineering", SystemRegistry.get_department_handle("Engineering"))

# 2. Setup CEO & App
ceo = CEO("Eddie")
trading_desk = TradingApp("Global_Macro_Bot", cfo) # CFO owns the Trading App

# 3. Execution
print(trading_desk.run_strategy("Arbitrage_2026"))
