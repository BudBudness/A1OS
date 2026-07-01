import importlib
from pathlib import Path

class EndToEndTestOrchestrator:
    def __init__(self, generated_dir="build/generated"):
        self.generated_dir = Path(generated_dir)

    def discover_test_suites(self):
        # Discover all test_suite.py files within generated subsystems
        return sorted(list(self.generated_dir.glob("**/test_suite.py")))

    def execute_suite(self, suite_path):
        # Convert path to module import path (e.g. build.generated.agent.test_suite)
        relative_path = suite_path.relative_to(self.generated_dir.parent)
        module_str = ".".join(relative_path.parts[:-1]) + "." + suite_path.stem
        
        try:
            mod = importlib.import_module(module_str)
            # Standardize on finding a test function or running main
            suite_name = f"test_{suite_path.parent.name}_subsystem"
            if hasattr(mod, suite_name):
                getattr(mod, suite_name)()
            elif hasattr(mod, "test_suite"):
                getattr(mod, "test_suite")()
            print(f"[TEST-ORCHESTRATOR] Subsystem integration suite passed: {module_str}")
            return True
        except Exception as e:
            print(f"[TEST-ORCHESTRATOR] Subsystem integration suite failed: {module_str} -- Reason: {e}")
            return False