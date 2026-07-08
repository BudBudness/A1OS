import os
import json
import tempfile
from core.crypto import encrypt_data, decrypt_data

class BaseWorker:
    def __init__(self, name):
        self.name = name
        self.file_path = f"data/{name}_state.json"
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_state(self, state):
        raw_json = json.dumps(state)
        encrypted = encrypt_data(raw_json)
        fd, path = tempfile.mkstemp(dir=os.path.dirname(self.file_path))
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(encrypted)
        os.replace(path, self.file_path)

    def load_state(self):
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as f:
                encrypted = f.read()
            raw_json = decrypt_data(encrypted)
            return json.loads(raw_json)
        except Exception:
            return {}
