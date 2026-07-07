import json
import importlib
import sys
import os

sys.path.append(os.getcwd())

class AgentRegistry:
    def __init__(self, registry_path="cfg/registry.json"):
        self.registry_path = registry_path

    def get_workers(self):
        if not os.path.exists(self.registry_path):
            return {}

        with open(self.registry_path, 'r') as f:
            config = json.load(f)
        
        workers = {}
        for worker_name, module_path in config.get("workers", {}).items():
            try:
                module = importlib.import_module(module_path)
                class_name = "".join([p.capitalize() for p in worker_name.split('_')])
                worker_class = getattr(module, class_name)
                workers[worker_name.split('_')[0]] = worker_class()
            except Exception as e:
                print(f"Error loading {worker_name}: {e}")
        return workers
