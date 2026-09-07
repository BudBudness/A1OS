import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "factory"

root = Path("factory_runs") / product / "self_management"
root.mkdir(parents=True, exist_ok=True)

capabilities = [
    "system_health_analysis",
    "runtime_optimization",
    "architecture_review",
    "upgrade_planning",
    "technical_debt_detection",
    "performance_improvement",
    "configuration_optimization",
    "lifecycle_management",
    "continuous_improvement_tracking",
    "evolution_recommendation_generation"
]

managed_layers = [
    "global_ai_operator_runtime",
    "autonomous_business_operations",
    "global_control_plane",
    "network_intelligence_runtime",
    "platform_engineering_runtime",
    "production_observability_mesh",
    "autonomous_sre_runtime",
    "security_compliance_runtime",
    "data_ai_decision_runtime",
    "integration_bus"
]

manifest = {
    "runtime": "self_management_runtime",
    "version": "10.2",
    "generated": datetime.now(timezone.utc).isoformat(),
    "product": product,
    "status": "self_management_initialized",
    "architecture": "continuous_evolution_control_loop",
    "capabilities": capabilities,
    "managed_layers": managed_layers,
    "optimization_cycle": {
        "observe": True,
        "analyze": True,
        "recommend": True,
        "prioritize": True,
        "verify": True
    },
    "governance": {
        "change_tracking": True,
        "upgrade_planning": True,
        "approval_controls": True,
        "rollback_awareness": True
    },
    "execution_hooks": {
        "scan_runtime_health": True,
        "detect_improvements": True,
        "generate_upgrade_plans": True,
        "track_evolution_history": True,
        "produce_optimization_reports": True
    },
    "next_stage": [
        "autonomous_product_company_runtime",
        "global_market_intelligence_runtime",
        "factory_recursive_optimization"
    ]
}

(root / "SELF_MANAGEMENT_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY SELF-MANAGEMENT RUNTIME v10.2")
print("=" * 70)
print(f"Product: {product}")

for capability in capabilities:
    print("✓", capability)

print(f"Artifacts: {root}")
