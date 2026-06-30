import json
import os

class SovereignMemoryEngine:
    def __init__(self):
        self.db = {}
    def set(self, key, value):
        self.db[key] = value
        return True
    def get(self, key):
        return self.db.get(key, None)
