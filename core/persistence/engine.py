import json
import os

class StateManager:
    def __init__(self, storage_path="/data/data/com.termux/files/home/A1OS/data/state.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def save_state(self, task_id, state_data):
        try:
            current_state = self._load_all()
            current_state[task_id] = state_data
            with open(self.storage_path, 'w') as f:
                json.dump(current_state, f)
            return True
        except Exception:
            return False

    def _load_all(self):
        if not os.path.exists(self.storage_path):
            return {}
        with open(self.storage_path, 'r') as f:
            return json.load(f)

    def get_state(self, task_id):
        return self._load_all().get(task_id)
