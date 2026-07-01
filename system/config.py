import json
import os

class ConfigManager:
    def __init__(self, config_path="~/A1OS/data/config.json"):
        self.config_path = os.path.expanduser(config_path)
        self.settings = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.settings.get(key, default)
