import threading
import time
from .queue_manager import SovereignTaskQueue
from .tasks import SystemTaskRegistry

class SovereignWorkflowEngine:
    def __init__(self):
        self.queue = SovereignTaskQueue()
        self.registry = SystemTaskRegistry()
        self.is_running = False
        self._worker = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._worker = threading.Thread(target=self._process_loop, daemon=True)
            self._worker.start()
            print("[WORKFLOW-ENGINE] Asynchronous task worker thread active.")

    def submit(self, task_name, payload=None):
        self.queue.push(task_name, payload or {})

    def _process_loop(self):
        while self.is_running:
            task = self.queue.pop(timeout=0.5)
            if task:
                name, payload = task["name"], task["payload"]
                print(f"[WORKFLOW-EXEC] Dispatching sequence item: {name}")
                handler = self.registry.get_handler(name)
                if handler:
                    try:
                        handler(payload)
                    except Exception as e:
                        print(f"[WORKFLOW-ERR] Task execution crash on '{name}': {e}")
                else:
                    print(f"[WORKFLOW-WARN] Unmapped workflow step dropped: {name}")

    def stop(self):
        self.is_running = False
        if self._worker:
            self._worker.join(timeout=2.0)