import sys, os
sys.path.append(os.path.expanduser("~/A1OS"))
from core.execution.v2.dispatcher.engine import DistributedDispatcher

def test():
    d = DistributedDispatcher()
    d.register("test_action", lambda data: "success")
    # Verify Policy
    try:
        d.dispatch({"task_id": "test", "action": "test_action", "data": {}})
        print("Integration: Passed")
    except Exception as e:
        print(f"Integration: Failed - {e}")

if __name__ == "__main__":
    test()
