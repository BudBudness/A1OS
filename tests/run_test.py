import sys
import os

# Dynamically add A1OS root to the path
sys.path.append(os.path.expanduser("~/A1OS"))

from core.persistence.engine import StateManager

def main():
    manager = StateManager()
    manager.save_state("task_001", {"status": "pending", "payload": "verified"})
    state = manager.get_state("task_001")
    print(f"Verified State: {state}")

if __name__ == "__main__":
    main()
