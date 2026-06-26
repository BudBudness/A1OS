import queue
import threading
from datetime import datetime
from typing import List, Dict, Any

class EventBus:
    def __init__(self):
        self.queue = queue.Queue()
        self.history = []
        self.subscribers = {}
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def emit(self, event_type: str, data: Any):
        entry = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
        self.history.append(entry)
        if len(self.history) > 100:
            self.history.pop(0)
        self.queue.put(entry)
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(entry)

    def subscribe(self, event_type: str, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def get_history(self, limit: int = 20) -> List[Dict]:
        return self.history[-limit:]

    def _run(self):
        while self.running:
            try:
                event = self.queue.get(timeout=1)
                # Process event
            except queue.Empty:
                pass

    def stop(self):
        self.running = False
