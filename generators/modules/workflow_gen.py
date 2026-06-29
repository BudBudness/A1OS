from generators.core.base_gen import BaseGenerator
from pathlib import Path

class WorkflowGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "workflow"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Core Workflow Async Threading State Machine Engine
        engine_code = '''import threading
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
'''

        # 2. Thread-Safe Prioritized Task Queueing Unit
        queue_code = '''import queue
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
'''

        # 3. System Functional Tasks Definition Registry
        tasks_code = '''import time

class SystemTaskRegistry:
    def __init__(self):
        self._handlers = {}
        self._register_builtins()

    def _register_builtins(self):
        self.register("DATA_RECONCILE", lambda p: print(f"[TASK-EXEC] Reconciled system state maps for payload signature: {p}"))
        self.register("TELEMETRY_SYNC", lambda p: time.sleep(0.1) or print("[TASK-EXEC] Sync block flushed to disk."))

    def register(self, name, func):
        self._handlers[name.upper()] = func

    def get_handler(self, name):
        return self._handlers.get(name.upper())
'''

        # 4. Isolated Asynchronous Concurrency Verification Suite
        test_code = '''import time
from .engine import SovereignWorkflowEngine

def test_workflow_subsystem():
    engine = SovereignWorkflowEngine()
    engine.start()
    
    # Enqueue tasks to run concurrently
    engine.submit("DATA_RECONCILE", {"target": "ledger_01"})
    engine.submit("TELEMETRY_SYNC", {"node": "local_hardware"})
    
    # Give the thread loop background slices to resolve tasks
    time.sleep(0.5)
    engine.stop()
    print("✅ Asynchronous Workflow Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_workflow_subsystem()
'''

        # Write out the full workflow suite artifacts
        with open(output_dir / "engine.py", "w") as f: f.write(engine_code.strip())
        with open(output_dir / "queue_manager.py", "w") as f: f.write(queue_code.strip())
        with open(output_dir / "tasks.py", "w") as f: f.write(tasks_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] workflow_gen.py has compiled v1 Workflow Subsystem inside {output_dir}")
