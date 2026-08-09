import json
import logging
import os
from datetime import datetime

class PersistenceManager:
    def __init__(self, log_file="state.log"):
        # Ensure path is relative to this script's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(base_dir, "..", log_file)

    def save_state(self, action, result):
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "result": result
            }
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logging.error(f"Persistence Error: {e}")
