import time
from .interpreter import DeterministicInterpreter
from .registry import SovereignToolRegistry

class SovereignAgentCore:
    def __init__(self):
        self.state = {"status": "initialized", "cycle_count": 0}
        self.interpreter = DeterministicInterpreter()
        self.registry = SovereignToolRegistry()

    def execute_cycle(self, raw_input_string):
        self.state["cycle_count"] += 1
        print(f"[AGENT-CYCLE] Activating evaluation frame #{self.state['cycle_count']}")
        
        intent, params = self.interpreter.parse_intent(raw_input_string)
        if intent == "UNKNOWN":
            return {"status": "failed", "reason": "unparseable_command_structure"}
            
        tool = self.registry.get_tool(intent)
        if not tool:
            return {"status": "unmapped", "intent": intent, "params": params}
            
        try:
            execution_result = tool(params)
            return {"status": "success", "intent": intent, "result": execution_result}
        except Exception as e:
            return {"status": "execution_error", "error": str(e)}