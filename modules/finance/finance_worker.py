from core.worker_base import BaseWorker

class FinanceWorker(BaseWorker):
    def __init__(self):
        super().__init__("finance")

    def process_task(self, task):
        state = self.load_state()
        state["last_task"] = task.get("data")
        self.save_state(state)
        return f"Finance processed: {task.get('data')}"
