from core.worker_base import BaseWorker

class OpsWorker(BaseWorker):
    def __init__(self):
        super().__init__("ops")

    def process_task(self, task):
        state = self.load_state()
        state["last_task"] = task.get("data")
        self.save_state(state)
        return f"Ops processed: {task.get('data')}"
