import importlib
import os
from typing import Dict, Any

class DomainPackLoader:
    def __init__(self, packs_dir: str = "domain_packs"):
        self.packs_dir = packs_dir
        self.loaded = {}

    def load(self, pack_name: str) -> Dict[str, Any]:
        if pack_name in self.loaded:
            return self.loaded[pack_name]
        try:
            module = importlib.import_module(f"domain_packs.{pack_name}")
            self.loaded[pack_name] = {"name": pack_name, "module": module, "loaded": True}
            return self.loaded[pack_name]
        except ImportError:
            return {"name": pack_name, "error": "Not found", "loaded": False}

    def list_available(self) -> list:
        files = os.listdir(self.packs_dir)
        return [f[:-3] for f in files if f.endswith('.py') and not f.startswith('__')]
