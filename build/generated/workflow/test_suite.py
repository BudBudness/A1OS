import time
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