import sys
import os

# Dynamically add A1OS root
sys.path.append(os.path.expanduser("~/A1OS"))

from core.execution.v2.dispatcher.engine import DistributedDispatcher

def mock_handler(data):
    return {"status": "processed", "payload": data}

def main():
    dispatcher = DistributedDispatcher()
    dispatcher.register("test_action", mock_handler)
    
    # 1. Test standard dispatch and persistence
    decision = {"task_id": "task_999", "action": "test_action", "data": {"key": "value"}}
    result = dispatcher.dispatch(decision)
    print(f"Dispatch Result: {result}")
    
    # 2. Verify persistence
    persisted = dispatcher.state.get_state("task_999")
    print(f"Persisted State: {persisted}")

if __name__ == "__main__":
    main()
