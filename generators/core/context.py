import os
from pathlib import Path

class GenerationContext:
    def __init__(self, schema_data: dict, root_dir):
        self.schema = schema_data
        self.root = Path(root_dir).resolve()
        self.endpoints = []
        self.shared_state = {}
        
        # Legacy key maps expected by older generator modules
        self.output_dir = str(self.root / "build/generated")
        self.project_root = str(self.root)

    def register_endpoint(self, method: str, path: str, handler: str, module: str):
        self.endpoints.append({
            "method": method,
            "path": path,
            "handler": handler,
            "module": module
        })

    # Dictionary Emulation Layer for Legacy Modules (context["key"])
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.schema:
            return self.schema[key]
        raise KeyError(f"GenerationContext key '{key}' not found in attributes or schema declarations.")

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
