from core.worker_base import BaseWorker

class AnalyticsWorker(BaseWorker):
    def __init__(self):
        super().__init__("analytics")

    def process_task(self, task):
        action = task.get("action", "metrics")
        state = self.load_state()
        
        if action == "aggregate":
            event = task.get("event", {})
            target = event.get("target", "unknown")
            state[target] = state.get(target, 0) + 1
            self.save_state(state)
            return {"status": "aggregated"}
            
        elif action == "metrics":
            return {"event_counts": state}
            
        return {"error": "Unknown Analytics action"}
