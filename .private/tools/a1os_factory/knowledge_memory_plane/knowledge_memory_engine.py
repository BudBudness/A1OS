from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 knowledge_memory_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "knowledge_memory"

layers = {
    "knowledge_graph": {},
    "documents": {},
    "semantic_index": {},
    "memory": {},
    "retrieval": {},
    "governance": {},
    "learning": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.7",
    "status": "knowledge_memory_ready",
    "generated": datetime.utcnow().isoformat(),
    "components": list(layers.keys())
}

(root / "KNOWLEDGE_MEMORY_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Knowledge Memory Plane Generated: {product}")
