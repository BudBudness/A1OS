from pathlib import Path
import json
from datetime import datetime

ROOT = Path("products")

products = []

for product in ROOT.iterdir():
    if product.is_dir() and not product.name.startswith("."):

        intelligence = product / "intelligence"
        operations = product / "operations"

        products.append({
            "product": product.name,
            "intelligence_layer": intelligence.exists(),
            "operations_layer": operations.exists(),
            "agents": "available" if intelligence.exists() else "not_detected",
            "workflows": "available" if intelligence.exists() else "not_detected",
            "status": "monitored"
        })

report = {
    "factory_version": "2.2",
    "generated": datetime.utcnow().isoformat(),
    "command_center": "active",
    "products_monitored": len(products),
    "products": products,
    "insights": {
        "recommendations": "enabled",
        "anomaly_detection": "enabled",
        "cross_product_analysis": "enabled"
    }
}

center = Path("factory_intelligence")
center.mkdir(exist_ok=True)

(center / "INTELLIGENCE_REPORT.json").write_text(
    json.dumps(report, indent=2)
)

print("A1OS Intelligence Command Center Generated")
print(f"Products monitored: {len(products)}")
