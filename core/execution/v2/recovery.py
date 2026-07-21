from core.persistence.engine import StateManager

class RecoveryEngine:
    def __init__(self):
        self.state = StateManager()

    def reconcile(self):
        # Deferred import to break circular dependency
        from core.execution.v2.dispatcher.engine import DistributedDispatcher
        self.dispatcher = DistributedDispatcher()
        all_tasks = self.state._load_all()
        for tid, data in all_tasks.items():
            if data.get("status") == "dispatched":
                self.dispatcher.dispatch(data.get("decision"))
