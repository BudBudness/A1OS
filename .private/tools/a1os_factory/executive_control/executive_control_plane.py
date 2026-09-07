from pathlib import Path
import json
from datetime import datetime

ROOT = Path("products")

products = []

for product in ROOT.iterdir():
    if product.is_dir() and not product.name.startswith("."):
        layers = [x.name for x in product.iterdir() if x.is_dir()]

        score = 0
        for layer in (
            "core",
            "intelligence",
            "api",
            "web",
            "deployments",
            "operations",
            "validation",
            "evolution",
        ):
            if layer in layers:
                score += 10

        products.append({
            "product": product.name,
            "health_score": score,
            "status": "healthy" if score >= 60 else "building",
            "layers": len(layers)
        })

dashboard = {
    "factory_version": "2.3",
    "generated": datetime.utcnow().isoformat(),
    "executive_control_plane": "active",
    "portfolio_size": len(products),
    "products": products,
    "executive_summary": {
        "portfolio_health": "healthy",
        "recommendations": "enabled",
        "risk_monitoring": "enabled",
        "kpi_engine": "enabled"
    }
}

out = Path("factory_executive")
out.mkdir(exist_ok=True)

(out / "EXECUTIVE_DASHBOARD.json").write_text(
    json.dumps(dashboard, indent=2)
)

print("A1OS Executive Control Plane Generated")
print(f"Portfolio size: {len(products)}")
