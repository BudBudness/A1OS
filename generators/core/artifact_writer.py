import os
import hashlib
from pathlib import Path
import json
from datetime import datetime

class ArtifactWriter:
    def __init__(self, root_dir):
        self.root = Path(root_dir).resolve()
        self.manifest_path = self.root / "build/generated/manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text())
            except Exception:
                return {}
        return {}

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def write(self, target: str, content: str, generator_name: str):
        target_path = (self.root / target).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        new_hash = self._compute_hash(content)
        old_hash = self.manifest.get(target, {}).get("hash")

        if target_path.exists() and old_hash == new_hash:
            # Skip writing if content is completely identical
            return False

        # Execute atomic write via temporary swap
        tmp_path = target_path.with_suffix(f".tmp_{generator_name}")
        tmp_path.write_text(content, encoding='utf-8')
        if target_path.exists():
            # Backup old deployment version silently if needed
            pass
        tmp_path.replace(target_path)

        # Update tracking manifest entry
        self.manifest[target] = {
            "generator": generator_name,
            "hash": new_hash,
            "updated_at": datetime.now().isoformat()
        }
        self._save_manifest()
        return True

    def _save_manifest(self):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(self.manifest, indent=4))
