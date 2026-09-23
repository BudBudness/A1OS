"""Shared deterministic runtime for lightweight A1OS Product Factory engines."""
from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

@dataclass(frozen=True)
class EngineSpec:
    name: str
    capability: str
    artifact_kind: str
    requires_approval: bool = False

class FactoryEngine:
    def __init__(self, spec: EngineSpec) -> None:
        self.spec = spec

    def plan(self, product: str, requirements: Mapping[str, Any]) -> dict[str, Any]:
        product = product.strip()
        if not product:
            raise ValueError("product is required")
        req = dict(requirements)
        selected = list(req.get("capabilities", []))
        if selected and self.spec.capability not in selected:
            return {"engine": self.spec.name, "product": product, "selected": False,
                    "reason": "capability_not_requested"}
        payload = {"engine": self.spec.name, "capability": self.spec.capability,
                   "product": product, "artifact_kind": self.spec.artifact_kind,
                   "requires_approval": self.spec.requires_approval, "requirements": req,
                   "status": "planned"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        payload["plan_id"] = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return payload

    def run(self, product: str, requirements: Mapping[str, Any] | None = None,
            output_root: Path | None = None) -> dict[str, Any]:
        plan = self.plan(product, requirements or {})
        if plan.get("selected") is False:
            return plan
        target = (output_root or Path("factory_runs")) / product / "engines"
        target.mkdir(parents=True, exist_ok=True)
        path = target / f"{self.spec.name}.json"
        plan["generated_at"] = datetime.now(timezone.utc).isoformat()
        plan["artifact"] = str(path)
        path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return plan

def cli(engine: FactoryEngine) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product")
    parser.add_argument("--requirements", type=Path)
    args = parser.parse_args()
    requirements = json.loads(args.requirements.read_text(encoding="utf-8")) if args.requirements else {}
    print(json.dumps(engine.run(args.product, requirements), indent=2))

def make_engine(name: str, capability: str, artifact_kind: str = "capability-contract",
                requires_approval: bool = False) -> FactoryEngine:
    return FactoryEngine(EngineSpec(name, capability, artifact_kind, requires_approval))
