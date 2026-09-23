"""Deterministic artifact generation pipeline for frontend verticals."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

TARGETS = ("frontend","workflows","forms","integrations","tests","documentation","deployment-contract")

def generate(product: str, requirements: dict, output: Path | None = None) -> dict:
    if not product.strip():
        raise ValueError("product is required")
    if not isinstance(requirements, dict):
        raise TypeError("requirements must be an object")
    requested = set(requirements.get("artifacts", TARGETS))
    artifacts = [item for item in TARGETS if item in requested]
    manifest = {"plane":"code_generation_pipeline","version":"2.1","product":product,
                "generated":datetime.now(timezone.utc).isoformat(),"status":"generated",
                "customized":True,"artifact_targets":artifacts,"requirements":requirements}
    destination = output or Path("factory_runs")/product/"CODE_GENERATION_MANIFEST.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 code_generation_engine.py PRODUCT REQUIREMENTS_JSON")
        raise SystemExit(2)
    print(json.dumps(generate(sys.argv[1],json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")),),indent=2))
