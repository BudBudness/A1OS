import sqlite3
from workflow.engine import WorkflowEngine

# 1. Create and Run Pipeline
tid = WorkflowEngine.create_task("CFO", "CEO", "Finance", 1, 10000.0)
WorkflowEngine.run_pipeline(tid)

# 2. Query SQLite directly to verify Persistence
conn = sqlite3.connect("/data/data/com.termux/files/home/A1OS/audit.db")
row = conn.execute("SELECT data FROM tasks WHERE id=?", (tid,)).fetchone()
conn.close()

if row:
    print(f"Persistence Success: Task {tid} found in audit.db")
else:
    print("Persistence Failed: Database empty.")
