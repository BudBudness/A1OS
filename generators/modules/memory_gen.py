import os
from generators.core.base_gen import BaseGenerator

class Generator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)
        self.name = "memory"
        self.dependencies = ["api"]

    def generate(self):
        artifacts = []
        core_src = """import json
import os

class SovereignMemoryEngine:
    def __init__(self):
        self.db = {}
    def set(self, key, value):
        self.db[key] = value
        return True
    def get(self, key):
        return self.db.get(key, None)
"""
        routes_src = """from api.router import SovereignAPIRouter
from memory.core import SovereignMemoryEngine

engine = SovereignMemoryEngine()

@SovereignAPIRouter.register_route("/memory/store", method="POST")
def store_data(body):
    if not body or "key" not in body or "value" not in body:
        return 400, {"status": "ERROR", "message": "Missing key or value"}
    engine.set(body["key"], body["value"])
    return 200, {"status": "SUCCESS", "stored": body["key"]}

@SovereignAPIRouter.register_route("/memory/retrieve", method="POST")
def retrieve_data(body):
    if not body or "key" not in body:
        return 400, {"status": "ERROR", "message": "Missing key"}
    val = engine.get(body["key"])
    return 200, {"status": "SUCCESS", "key": body["key"], "value": val}
"""
        artifacts.append(self.emit_file("memory", "core.py", core_src))
        artifacts.append(self.emit_file("memory", "memory_routes.py", routes_src))
        return artifacts
