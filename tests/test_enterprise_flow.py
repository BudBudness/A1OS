from organization.departments.finance import FinanceDepartment
from applications.finance_app import FinanceApp
from system.registry import SystemRegistry

# 1. Register the Department (Infrastructure Init)
finance_dept = FinanceDepartment()
SystemRegistry.register_department("Finance", finance_dept)

# 2. Run the App (Governance & Execution)
fin_app = FinanceApp()
print(f"Transaction 1: {fin_app.run(5000, 'Vendor_A', 'Hosting')}")
print(f"Transaction 2: {fin_app.run(999999, 'Vendor_B', 'Overdraft')}")

# 3. Verify Persistence
import sqlite3, os
conn = sqlite3.connect(os.path.expanduser("~/A1OS/data/audit.db"))
logs = conn.execute("SELECT * FROM audit").fetchall()
print(f"\nTotal Audit Logs: {len(logs)}")
for log in logs: print(log)
