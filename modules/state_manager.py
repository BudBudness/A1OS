import json
import os

class StateManager:
    @staticmethod
    def save_state(module_name, state_data):
        with open(f"data/{module_name}.json", "w") as f:
            json.dump(state_data, f)

    @staticmethod
    def load_state(module_name):
        if not os.path.exists(f"data/{module_name}.json"):
            return {}
        with open(f"data/{module_name}.json", "r") as f:
            return json.load(f)
