
import json
import os

class CheckpointManager:
    def __init__(self, path: str = "checkpoints/"):
        self.path = path
        os.makedirs(path, exist_ok=True)
        
    def save(self, task_id: str, state: dict):
        with open(f"{self.path}{task_id}.json", "w") as f:
            json.dump(state, f)
            
    def load(self, task_id: str) -> dict:
        with open(f"{self.path}{task_id}.json", "r") as f:
            return json.load(f)

