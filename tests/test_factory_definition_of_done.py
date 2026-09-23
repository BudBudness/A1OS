import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def _roadmap():
    return json.loads((ROOT / "IMPLEMENTATION_ROADMAP.json").read_text())

def test_factory_has_37_roadmap_engines():
    roadmap = _roadmap()
    assert roadmap["engines"] == 37
    assert len(roadmap["roadmap"]) == 37
    for item in roadmap["roadmap"]:
        path = ROOT / item["engine"]
        assert path.is_file()
        assert item["status"] == "IMPLEMENTED"

def test_all_37_engines_are_callable_and_evidence_producing(tmp_path):
    sys.path.insert(0, str(ROOT))
    requirements = {"capabilities": [], "roles": ["owner"], "features": ["smoke-test"]}
    roadmap = _roadmap()
    seen = set()
    for item in roadmap["roadmap"]:
        module_path = item["engine"].removesuffix(".py").replace("/", ".")
        module = importlib.import_module(module_path)
        engine = getattr(module, "ENGINE")
        assert engine.spec.name not in seen
        seen.add(engine.spec.name)
        plan = engine.plan("dod-smoke", requirements)
        assert plan["status"] == "planned"
        assert plan["plan_id"]
        artifact = engine.run("dod-smoke", requirements, tmp_path)
        assert artifact["status"] == "planned"
        assert Path(artifact["artifact"]).is_file()
    assert len(seen) == 37

def test_vertical_generator_materializes_customized_frontend(tmp_path):
    sys.path.insert(0, str(ROOT))
    from tools.a1os_factory.vertical_os_generator_plane.vertical_os_generator_engine import generate
    target = generate("demo-product", {"capabilities": ["forms"], "roles": ["owner"]}, tmp_path)
    assert (target / "A1OS_VERTICAL.json").is_file()
    assert all((target / folder).is_dir() for folder in ("config","pages","components","workflows","forms","integrations","state","assets","tests"))
    assert "forms" in json.loads((target / "A1OS_VERTICAL.json").read_text())["requirements"]["capabilities"]

def test_generated_vertical_passes_real_validation_and_build(tmp_path):
    sys.path.insert(0, str(ROOT))
    from tools.a1os_factory.vertical_os_generator_plane.vertical_os_generator_engine import generate
    from tools.a1os_factory.validation.validation_engine import validate_product
    from tools.a1os_factory.real_build_executor.build_executor_engine import execute
    products = tmp_path / "products"
    evidence = tmp_path / "evidence"
    generate("e2e-product", {"capabilities": ["forms","workflows"], "roles": ["owner"]}, products)
    report = validate_product("e2e-product", products)
    assert report["status"] == "healthy", report
    build = execute("e2e-product", products, evidence)
    assert build["status"] == "built", build
    assert (evidence / "e2e-product" / "BUILD_EXECUTOR_MANIFEST.json").is_file()
    from tools.a1os_factory.code_generation_pipeline.code_generation_engine import generate as generate_code
    generated = generate_code("e2e-product", {"artifacts": ["frontend", "forms"]}, evidence / "code")
    assert generated["artifact_targets"] == ["frontend", "forms"]
    assert (evidence / "code" / "FRONTEND_CONTRACT.json").is_file()
    assert (evidence / "code" / "FORMS_CONTRACT.json").is_file()

def test_existing_products_have_manifests():
    for name in ("little-oaks", "legal", "charity"):
        path = ROOT / "products" / "verticals" / name
        assert path.is_dir()
        assert (path / "A1OS_VERTICAL.json").is_file()

def test_control_plane_command_is_allowlisted():
    text = (ROOT / "core/control_plane/app.py").read_text()
    assert "ALLOWED_COMMANDS" in text
    assert "create_subprocess_shell" not in text
    assert "shell=True" not in text
    assert '"/bin/sh"' not in text
    assert "execution_policy" in text

def test_legacy_jarvis_and_mcp_are_absent_from_working_tree():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            data = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lowered = data.lower()
        assert "jarvis" not in lowered, path
        assert "mcp" not in lowered, path
