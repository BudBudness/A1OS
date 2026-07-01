from core.bus import EventBus
from core.memory import MemoryManager
from core.reasoner import ReasoningEngine
from core.governance import CircuitBreaker

class Orchestrator:
    def __init__(self):
        self.memory = MemoryManager()
        self.reasoner = ReasoningEngine()
        self.governance = CircuitBreaker()
        EventBus.subscribe("TaskRequested", self.handle_task)

    def handle_task(self, data):
        try:
            # 1. Governance Check
            self.governance.validate(data.get("type"), data)
            
            # 2. Reasoning
            steps = self.reasoner.decompose(data.get("goal"))
            
            # 3. Execution & Memory
            self.memory.record_decision(data.get("type"), data, "SUCCESS")
            print(f"Orchestrator: Executed task via {steps}")
        except Exception as e:
            print(f"Orchestrator: HALTED - {e}")
