import json, os

class PersistenceManager:
    def __init__(self, path="~/A1OS/data/state.json"):
        self.path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
    
    def save_state(self, key, value):
        data = {}
        if os.path.exists(self.path):
            with open(self.path, 'r') as f: data = json.load(f)
        data[key] = value
        with open(self.path, 'w') as f: json.dump(data, f)
