import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 reasoning_decision_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "reasoning_decision_intelligence"

folders = [
    "reasoning_models",
    "decision_graphs",
    "policy_reasoning",
    "recommendations",
    "planning",
    "causal_analysis",
    "scenario_reasoning",
    "executive_intelligence",
    "automation_logic",
    "governance"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "autonomous_reasoning_decision_intelligence",
    "version": "5.7",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "reasoning_intelligence_ready",
    "capabilities": [
        "reasoning_engine_foundations",
        "decision_graph_intelligence",
        "policy_reasoning",
        "recommendation_generation",
        "autonomous_planning",
        "causal_analysis",
        "scenario_reasoning",
        "executive_decision_support"
    ]
}

(root / "REASONING_DECISION_INTELLIGENCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Reasoning Decision Intelligence Plane Generated: {product}")
