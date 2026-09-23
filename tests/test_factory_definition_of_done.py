import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def test_factory_has_37_roadmap_engines():
    roadmap = json.loads((ROOT / "IMPLEMENTATION_ROADMAP.json").read_text())
    assert roadmap["engines"] == 37
    assert len(roadmap["roadmap"]) == 37
    for item in roadmap["roadmap"]:
        path = ROOT / item["engine"]
        assert path.is_file()
        assert item["status"] == "IMPLEMENTED"

def test_factory_engines_are_deterministic_contracts():
    sys.path.insert(0, str(ROOT))
    from tools.a1os_factory.engine_runtime import make_engine
    engine = make_engine("test", "test-capability")
    requirements = {"capabilities": ["test-capability"], "roles": ["owner"]}
    one = engine.plan("demo", requirements)
    two = engine.plan("demo", requirements)
    assert one["plan_id"] == two["plan_id"]

def test_vertical_generator_materializes_customized_frontend(tmp_path):
    sys.path.insert(0, str(ROOT))
    from tools.a1os_factory.vertical_os_generator_plane.vertical_os_generator_engine import generate
    target = generate("demo-product", {"capabilities": ["forms"], "roles": ["owner"]}, tmp_path)
    assert (target / "A1OS_VERTICAL.json").is_file()
    assert (target / "pages").is_dir()
    assert (target / "tests").is_dir()
    assert "forms" in json.loads((target / "A1OS_VERTICAL.json").read_text())["requirements"]["capabilities"]

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
