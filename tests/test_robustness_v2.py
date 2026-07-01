from workflow.engine import WorkflowEngine
import sqlite3, json

# 1. Create a task
tid = WorkflowEngine.create_task("CFO", "CEO", "Finance", 1, 50000.0)

# 2. Simulate failure at BUDGET_CHECK
conn = sqlite3.connect("/data/data/com.termux/files/home/A1OS/audit.db")
task_data = json.loads(conn.execute("SELECT data FROM tasks WHERE id=?", (tid,)).fetchone()[0])
task_data['checkpoint'] = 'BUDGET_CHECK'
conn.execute("REPLACE INTO tasks VALUES (?,?)", (tid, json.dumps(task_data)))
conn.commit(); conn.close()

# 3. Resume the pipeline
WorkflowEngine.run_pipeline(tid)

# 4. Verify by fetching FRESH data from DB
task = WorkflowEngine.get_task(tid)
print(f"Task {tid} final status: {task.status}")
print(f"Final Checkpoint: {task.checkpoint}")
