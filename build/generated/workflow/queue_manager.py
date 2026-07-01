import queue
import time

class SovereignTaskQueue:
    def __init__(self):
        self._queue = queue.Queue()

    def push(self, task_name, payload):
        item = {"name": task_name.upper(), "payload": payload, "enqueued_at": time.time()}
        self._queue.put(item)
        print(f"[WORKFLOW-QUEUE] Registered transactional item: '{task_name.upper()}'")

    def pop(self, timeout=1.0):
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None