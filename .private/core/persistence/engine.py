import json
import os
from pathlib import Path

class StateManager:
    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = (
                Path(__file__).resolve().parents[2]
                / "data"
                / "state.json"
            )

        self.storage_path = str(storage_path)
        parent = os.path.dirname(self.storage_path)

        if parent:
            os.makedirs(parent, exist_ok=True)

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
