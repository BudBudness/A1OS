from core.execution.v2.dispatcher.engine import DistributedDispatcher

class ResearchSynthesizer:
    def __init__(self):
        self.dispatcher = DistributedDispatcher()

    def synthesize(self, topic, context=None):
        # Dispatches a research action that uses external AI reasoning tools
        decision = {"task_id": "res_001", "action": "process_data", "data": {"topic": topic}}
        return self.dispatcher.dispatch(decision, context=context)
