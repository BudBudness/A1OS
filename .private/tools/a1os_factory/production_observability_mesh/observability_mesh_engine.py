import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "observability_mesh"

components = {
    "metrics": [
        "prometheus",
        "metrics_registry",
        "service_metrics"
    ],
    "logging": [
        "loki",
        "log_pipeline",
        "log_retention"
    ],
    "visualization": [
        "grafana",
        "dashboards",
        "reports"
    ],
    "alerting": [
        "rules",
        "notifications",
        "incident_events"
    ],
    "ai_operations": [
        "anomaly_detection",
        "health_scoring",
        "prediction_models"
    ]
}

for category, items in components.items():
    for item in items:
        (root / category / item).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "production_observability_mesh",
    "version": "8.4",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "observability_initialized",
    "capabilities": [
        "metrics_collection",
        "log_aggregation",
        "dashboard_generation",
        "alert_management",
        "ai_operations_monitoring"
    ],
    "components": components
}

(root / "OBSERVABILITY_MESH_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY PRODUCTION OBSERVABILITY MESH v8.4")
print("=" * 70)
print(f"Product: {product}")

for component in components:
    print(" ✓", component)

print(root)
