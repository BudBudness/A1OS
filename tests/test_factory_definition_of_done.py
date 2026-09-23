import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def test_factory_has_37_roadmap_engines():
    roadmap = json.loads((ROOT / "IMPLEMENTATION_ROADMAP.json").read_text())
    assert roadmap["engines"] == 37
    assert len(roadmap["roadmap"]) == 37
    for item in roadmap["roadmap"]:
        assert (ROOT / item["engine"]).is_file()
        assert item["status"] == "IMPLEMENTED"

def test_factory_engines_are_deterministic_contracts():
    sys.path.insert(0, str(ROOT))
    from tools.a1os_factory.engine_runtime import make_engine
    engine = make_engine("test", "test-capability")
    one = engine.plan("demo", {"capabilities": ["test-capability"], "roles": ["owner"]})
    two = engine.plan("demo", {"capabilities": ["test-capability"], "roles": ["owner"]})
    assert one["plan_id"] == two["plan_id"]

def test_existing_products_have_evidence():
    requirements = {
        "little-oaks": ("A1OS_VERTICAL.json",),
        "legal": ("A1OS_VERTICAL.json", "release/RELEASE_STATUS.json", "validation/VALIDATION_REPORT.json"),
        "charity": ("A1OS_VERTICAL.json", "deployments/stramoswisdomcharityorg/PRODUCT.md"),
    }
    for name, candidates in requirements.items():
        path = ROOT / "products/verticals" / name
        assert path.is_dir()
        assert any((path / candidate).exists() for candidate in candidates)

def test_no_forbidden_control_plane_legacy():
    text = (ROOT / "core/control_plane/app.py").read_text().lower()
    assert ("j" + "arvis") not in text
    assert ("m" + "cp") not in text

def test_control_plane_command_is_allowlisted():
    text = (ROOT / "core/control_plane/app.py").read_text()
    assert "ALLOWED_COMMANDS" in text
    assert '"bash"' not in text
