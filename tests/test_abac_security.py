import sys, os
sys.path.append(os.path.expanduser("~/A1OS"))
from core.execution.v2.dispatcher.engine import DistributedDispatcher

def test():
    d = DistributedDispatcher()
    d.register("process_data", lambda data: "processed")
    
    # Test valid role (user)
    try:
        d.dispatch({"task_id": "t1", "action": "process_data", "data": {}}, context={"role": "user"})
        print("Success: Valid user role allowed")
    except Exception as e:
        print(f"Failed: {e}")

    # Test invalid role (system, not in policy for process_data)
    try:
        d.dispatch({"task_id": "t2", "action": "process_data", "data": {}}, context={"role": "guest"})
        print("Failed: Invalid role allowed")
    except PermissionError:
        print("Success: Unauthorized role blocked")

if __name__ == "__main__":
    test()
