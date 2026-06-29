import json, os
from pathlib import Path

class SchemaLoader:
    def __init__(self, schema_path):
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.validate()

    def validate(self):
        required = ["version", "runtime", "modules"]
        for key in required:
            if key not in self.schema:
                raise ValueError(f"Missing required key: {key}")
        return True

    def get_modules(self):
        return self.schema.get("modules", {})

    def get_runtime(self):
        return self.schema.get("runtime", {})

    def get_nodes(self):
        return self.schema.get("nodes", [])

if __name__ == "__main__":
    loader = SchemaLoader("schema/platform.json")
    print("✅ Schema loaded:", loader.schema["version"])
