import json, os, uuid, hashlib
from datetime import datetime

BASE = "/data/data/com.termux/files/home/A1OS"
class Task:
    def __init__(self, department, task_type, payload):
        self.id, self.department, self.task_type = str(uuid.uuid4()), department, task_type
        self.payload, self.status = payload, "PENDING"
        self.created_at, self.approval_state = datetime.now().isoformat(), "APPROVED"
        self.hash = hashlib.sha256(f"{self.id}{self.payload}".encode()).hexdigest()
    def save(self):
        with open(f"{BASE}/data/tasks/pending/{self.id}.json", 'w') as f: json.dump(self.__dict__, f)

class ExecutionEngine:
    def process_queue(self):
        pending = f"{BASE}/data/tasks/pending/"
        for filename in os.listdir(pending):
            path = os.path.join(pending, filename)
            with open(path, 'r') as f: task = json.load(f)
            if task["approval_state"] == "APPROVED":
                self.execute(task)
                os.rename(path, f"{BASE}/data/tasks/archive/{task['id']}.json")
    def execute(self, task):
        with open(f"{BASE}/data/ingest/logs/execution.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} | EXECUTING | {task['id']} | {task['task_type']}\n")

if __name__ == "__main__": ExecutionEngine().process_queue()
