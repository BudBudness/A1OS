import logging
import os
import importlib.util
from typing import Dict

logger = logging.getLogger("A1OS-LifecycleManager")

class LifecycleManager:
    def __init__(self, control_plane):
        self.cp = control_plane
        self.registry: Dict[str, any] = {}

    def scan_and_load(self, directory: str = "plugins"):
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                name = filename[:-3]
                path = os.path.join(directory, filename)
                self.load_plugin(name, path)

    def load_plugin(self, name: str, path: str):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.registry[name] = module
        logger.info(f"[LIFECYCLE] Plugin {name} loaded from {path}")

    def unload_plugin(self, name: str):
        if name in self.registry:
            del self.registry[name]
            logger.info(f"[LIFECYCLE] Plugin {name} terminated")
