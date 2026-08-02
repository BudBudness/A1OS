import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "data_ai_decision"

modules = {
    "data_ingestion": [
        "connectors",
        "pipelines",
        "validation"
    ],
    "analytics": [
        "metrics",
        "dashboards",
        "reports"
    ],
    "ai_models": [
        "prediction",
        "classification",
        "recommendations"
    ],
    "decision_engine": [
        "rules",
        "signals",
        "actions"
    ]
}

for group, items in modules.items():
    for item in items:
        (root / group / item).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "data_ai_decision_runtime",
    "version": "8.6",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "initialized",
    "capabilities": [
        "data_processing",
        "analytics_generation",
        "ai_model_management",
        "decision_intelligence",
        "recommendation_generation"
    ],
    "modules": modules
}

(root / "DATA_AI_DECISION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY DATA INTELLIGENCE & AI DECISION RUNTIME v8.6")
print("=" * 70)
print(f"Product: {product}")

for module in modules:
    print("✓", module)

print(root)
