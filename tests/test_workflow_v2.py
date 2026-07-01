from workflow.engine import WorkflowEngine

# 1. Create a governed task
tid = WorkflowEngine.create_task("CFO", "CEO", "Finance", 1, 50000.0)

# 2. Run the production pipeline
WorkflowEngine.run_pipeline(tid)

# 3. Verify object integrity
task = WorkflowEngine.get_task(tid)
print(f"Task: {tid} | Status: {task.status}")
print(f"Log Entries: {len(task.execution_log)}")
print(f"Audit Hash: {task.audit_hash[:16]}...")
