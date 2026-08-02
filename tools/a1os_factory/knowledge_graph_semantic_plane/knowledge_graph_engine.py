import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 knowledge_graph_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "knowledge_graph_semantic"

folders = [
    "entities",
    "relationships",
    "ontology",
    "semantic_index",
    "context_engine",
    "entity_resolution",
    "reasoning",
    "retrieval_intelligence",
    "federation",
    "governance"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "knowledge_graph_semantic_intelligence",
    "version": "5.6",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "semantic_intelligence_ready",
    "capabilities": [
        "enterprise_knowledge_graph",
        "semantic_relationship_mapping",
        "ontology_management",
        "entity_resolution",
        "context_reasoning",
        "semantic_retrieval",
        "knowledge_federation",
        "ai_reasoning_foundations"
    ]
}

(root / "KNOWLEDGE_GRAPH_SEMANTIC_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Knowledge Graph Semantic Plane Generated: {product}")
