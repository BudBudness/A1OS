import json
import hashlib
import time
from pathlib import Path

class ReleaseManifestGenerator:
    def __init__(self, build_dir):
        self.build_dir = Path(build_dir)

    def generate_sbom(self, version):
        manifest = {
            "version": version,
            "compiled_at": time.time(),
            "components": []
        }
        
        for p in self.build_dir.rglob("*.py"):
            if p.is_file():
                with open(p, "rb") as f:
                    h = hashlib.sha256(f.read()).hexdigest()
                manifest["components"].append({
                    "path": str(p.relative_to(self.build_dir.parent)),
                    "sha256": h
                })
                
        return manifest