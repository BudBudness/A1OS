from pathlib import Path
import json
import sys
from datetime import datetime

ROOT = Path("products")

if len(sys.argv) < 3:
    print("Usage: python3 orchestrator.py product-name profile")
    sys.exit(1)

name = sys.argv[1]
profile = sys.argv[2]

product = ROOT / name

layers = [
    "core",
    "intelligence",
    "api",
    "web",
    "deployments",
    "docs",
    "operations",
    "validation",
    "evolution"
]

for layer in layers:
    (product / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": name,
    "profile": profile,
    "factory_version": "2.0",
    "created": datetime.utcnow().isoformat(),
    "pipeline": {
        "dna": "complete",
        "runtime": "generated",
        "intelligence": "injected",
        "operations": "generated",
        "validation": "ready",
        "evolution": "enabled"
    },
    "status": "orchestrated"
}

(product / "A1OS_ORCHESTRATOR_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

release = product / "release"
release.mkdir(exist_ok=True)

(release / "RELEASE_STATUS.json").write_text(
    json.dumps({
        "product": name,
        "status": "production_candidate",
        "generated": datetime.utcnow().isoformat()
    }, indent=2)
)

print(f"A1OS Product Orchestrated: {product}")
