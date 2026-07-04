
import json
from pathlib import Path

class CheckpointManager:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        
    def save_checkpoint(self, task_id: str, state: dict):
        checkpoint_file = self.storage_path / f"{task_id}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(state, f)
            
    def load_checkpoint(self, task_id: str) -> dict:
        checkpoint_file = self.storage_path / f"{task_id}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, "r") as f:
                return json.load(f)
        return {}

