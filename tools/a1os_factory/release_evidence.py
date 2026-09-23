"""End-to-end evidence runner for the A1OS Product Factory."""
from __future__ import annotations
import importlib, json, tempfile
from pathlib import Path
from tools.a1os_factory.code_generation_pipeline.code_generation_engine import generate as generate_code
from tools.a1os_factory.real_build_executor.build_executor_engine import execute
from tools.a1os_factory.validation.validation_engine import validate_product
from tools.a1os_factory.vertical_os_generator_plane.vertical_os_generator_engine import generate

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "IMPLEMENTATION_ROADMAP.json"

def run() -> dict:
    roadmap = json.loads(ROADMAP.read_text(encoding="utf-8"))
    requirements = {"capabilities": [], "roles": ["owner"], "features": ["release-evidence"], "artifacts": ["frontend","workflows","forms","integrations","tests","documentation","deployment-contract"]}
    engine_results = []
    with tempfile.TemporaryDirectory(prefix="a1os-factory-") as work:
        work_root = Path(work)
        for item in roadmap["roadmap"]:
            module = importlib.import_module(item["engine"].removesuffix(".py").replace("/", "."))
            engine = module.ENGINE
            result = engine.run("release-evidence", requirements, work_root)
            engine_results.append({"engine": engine.spec.name, "status": result["status"], "artifact": result["artifact"]})
        products = work_root / "products"
        evidence = work_root / "evidence"
        generate("release-evidence", requirements, products)
        code = generate_code("release-evidence", requirements, evidence / "code")
        validation = validate_product("release-evidence", products)
        build = execute("release-evidence", products, evidence / "build")
        result = {
            "status": "PASS" if validation["status"] == "healthy" and build["status"] == "built" and len(engine_results) == 37 and code["status"] == "generated" else "FAIL",
            "engine_count": len(engine_results),
            "engines": engine_results,
            "code_generation": code,
            "validation": validation,
            "build": build,
        }
        output = ROOT / "factory_runs" / "release" / "DEFINITION_OF_DONE_EVIDENCE.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
