import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 ecosystem_marketplace_generator_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "ecosystem_marketplace"

folders = [
    "catalog",
    "editions",
    "pricing",
    "packaging",
    "deployment_bundles",
    "licensing",
    "subscriptions",
    "partners",
    "marketplace",
    "customer_portal",
    "analytics"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "ecosystem_marketplace_generator",
    "version": "6.1",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "commercialization_ready",
    "capabilities": [
        "product_packaging",
        "saas_edition_generation",
        "pricing_foundations",
        "licensing",
        "subscriptions",
        "marketplace_generation",
        "partner_ecosystem"
    ]
}

(root / "ECOSYSTEM_MARKETPLACE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Ecosystem Marketplace Generator Plane Generated: {product}")
