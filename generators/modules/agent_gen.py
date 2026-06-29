from generators.core.base_gen import BaseGenerator
from pathlib import Path

class AgentGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "agent"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Main Sovereign Agent State & Decision Loop Engine
        core_agent = '''import time
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
'''

        # 2. Lexical Command Context and Intent Parser
        interpreter = '''class DeterministicInterpreter:
    def parse_intent(self, raw_text):
        cleaned = raw_text.strip().upper()
        if not cleaned:
            return "UNKNOWN", {}
            
        # Fast split for command/parameter boundaries
        parts = cleaned.split(" ", 1)
        command = parts[0]
        params = {}
        
        if len(parts) > 1:
            # Basic key-value pair syntax extraction helper (key=val)
            for pair in parts[1].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k.strip().lower()] = v.strip()
                    
        return command, params
'''

        # 3. Structural Tools and System Hook Registry
        registry = '''class SovereignToolRegistry:
    def __init__(self):
        self._registry = {}
        self._load_builtins()

    def _load_builtins(self):
        self.register_tool("PING", lambda p: "PONG")
        self.register_tool("ECHO", lambda p: p.get("msg", ""))

    def register_tool(self, name, func):
        self._registry[name.upper()] = func
        print(f"[AGENT-REGISTRY] Attached executable hook vector: '{name.upper()}'")

    def get_tool(self, name):
        return self._registry.get(name.upper())
'''

        # 4. Isolated Agent Core Component Integration Testing Suite
        test_suite = '''from .core_agent import SovereignAgentCore

def test_agent_subsystem():
    agent = SovereignAgentCore()
    
    # Test built-in ping routine execution
    res = agent.execute_cycle("PING")
    assert res["status"] == "success"
    assert res["result"] == "PONG"
    
    # Test parameter splitting logic sequence
    res_echo = agent.execute_cycle("ECHO msg=SovereignOS")
    assert res_echo["status"] == "success"
    assert res_echo["result"] == "SOVEREIGNOS"
    
    print("✅ Agent Execution Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_agent_subsystem()
'''

        # Atomically drop out the full agent runtime block definitions
        with open(output_dir / "core_agent.py", "w") as f: f.write(core_agent.strip())
        with open(output_dir / "interpreter.py", "w") as f: f.write(interpreter.strip())
        with open(output_dir / "registry.py", "w") as f: f.write(registry.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_suite.strip())
        
        print(f"[GENERATOR-COMPLETE] agent_gen.py has compiled v1 Agent Subsystem inside {output_dir}")
