from workflow.engine import WorkflowEngine
from workflow.security import LedgerSecurity
import sqlite3

# Initialize and create tasks
WorkflowEngine._init_db()
tid1 = WorkflowEngine.create_task("USER_A", "TARGET_1", "FINANCE", 1, 500)
tid2 = WorkflowEngine.create_task("USER_B", "TARGET_2", "FINANCE", 1, 1500)

# Verify Integrity
try:
    is_valid = WorkflowEngine.recover_state()
    print(f"Kernel Integrity: {is_valid}")
except Exception as e:
    print(e)

# Tamper Test
conn = sqlite3.connect("/data/data/com.termux/files/home/A1OS/audit.db")
conn.execute("UPDATE tasks SET data = 'TAMPERED' WHERE id = ?", (tid1,))
conn.commit(); conn.close()

try:
    WorkflowEngine.recover_state()
except Exception as e:
    print(f"Tamper Detection Triggered: {e}")
