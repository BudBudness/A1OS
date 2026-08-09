import json, os, uuid
class TaskQueue:
    QUEUE_FILE = "/tmp/a1os_queue.json"
    def push(self, cmd):
        tasks = self._load()
        tid = str(uuid.uuid4())
        tasks[tid] = {"cmd": cmd, "status": "pending"}
        self._save(tasks)
        return tid
    def _load(self):
        if os.path.exists(self.QUEUE_FILE):
            with open(self.QUEUE_FILE, "r") as f: return json.load(f)
        return {}
    def _save(self, tasks):
        with open(self.QUEUE_FILE, "w") as f: json.dump(tasks, f)
