import json, os, uuid, hashlib, shutil
from datetime import datetime
from governance.core import GovernanceCore
from core.execution.dispatcher import route_task
from core.lifecycle import ExecutionBroker, ExecutionRequest

BASE = "/data/data/com.termux/files/home/A1OS"

class ExecutionEngine:
    def __init__(self):
        self.governance = GovernanceCore()
        self.dlq = f"{BASE}/data/tasks/dlq/"
        os.makedirs(self.dlq, exist_ok=True)

    def process_queue(self):
        pending = f"{BASE}/data/tasks/pending/"
        for filename in os.listdir(pending):
            path = os.path.join(pending, filename)
            with open(path, 'r') as f: task = json.load(f)
            
            try:
                if self.governance.check_task(task):
                    request = ExecutionRequest(
                        command=f"route_task:{task.get("id", "unknown")}",
                        payload=task,
                        approval_token=task.get("approval_token"),
                        request_id=task.get("id"),
                    )
                    broker = ExecutionBroker(
                        executor=lambda _request: route_task(task)
                    )
                    result = broker.execute(request)
                    if result.state.value == "completed" and result.result:
                        self.log_exec(task, "SUCCESS")
                        shutil.move(path, f"{BASE}/data/tasks/archive/{task['id']}.json")
                    else:
                        raise Exception("Dispatch Failed")
            except Exception as e:
                self.log_exec(task, f"FAILED | {str(e)}")
                shutil.move(path, f"{self.dlq}/{task['id']}.json")

    def log_exec(self, task, status):
        with open(f"{BASE}/data/ingest/logs/execution.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} | {status} | {task['id']} | {task['task_type']}\n")

if __name__ == "__main__": ExecutionEngine().process_queue()
