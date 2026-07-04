import json
import os

class BaseModule:
    def __init__(self):
        self.name = self.__class__.__name__
        self.state_dir = "data"
        if not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)

    def save_state(self, state_data):
        with open(f"{self.state_dir}/{self.name}.json", "w") as f:
            json.dump(state_data, f)

    def load_state(self):
        path = f"{self.state_dir}/{self.name}.json"
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def get_status(self):
        return f"{self.name} is operational."

    def execute(self, action, **kwargs):
        raise NotImplementedError("Each module must implement an execute method.")
