from core.persistence.engine import StateManager

# Initialize and persist test data
manager = StateManager()
manager.save_state("task_001", {"status": "pending", "payload": "verified"})

# Retrieve and confirm
state = manager.get_state("task_001")
print(f"Verified State: {state}")
