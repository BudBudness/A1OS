import sqlite3
import os
from system.registry import SystemRegistry

class AuditDashboard:
    def __init__(self):
        self.db_path = os.path.expanduser("~/A1OS/data/audit.db")

    def run(self):
        print(f"\n--- Enterprise Health Dashboard (Dynamic) ---")
        
        # 1. Show Organizational KPIs (Real-time)
        print(f"{'Department':<15} | {'Budget':<10} | {'Spent':<10} | {'Status'}")
        print("-" * 50)
        # We iterate over registry departments (which we store in our own cache)
        for name in SystemRegistry._departments.keys():
            handle = SystemRegistry.get_department_handle(name)
            kpis = handle.get_status()
            print(f"{name:<15} | {kpis.get('budget', 0):<10} | {kpis.get('spent', 0):<10} | Active")

        # 2. Show Governance Audit Logs (Historical)
        print(f"\n--- Governance Audit Log ---")
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            logs = conn.execute("SELECT timestamp, worker, task, status FROM audit ORDER BY timestamp DESC LIMIT 5").fetchall()
            for log in logs:
                print(f"{log[0][11:19]} | {log[1]:<10} | {log[3]:<8} | {log[2]}")
            conn.close()
