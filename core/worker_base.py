import json
import os

class BaseWorker:
    def __init__(self, name):
        self.name = name
        self.data_dir = f"data/{name}"
        self.state_path = f"{self.data_dir}/state.json"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                try: return json.load(f)
                except: return {}
        return {"status": "initialized", "domain": self.name}

    def save_state(self, state):
        with open(self.state_path, 'w') as f: json.dump(state, f, indent=4)
