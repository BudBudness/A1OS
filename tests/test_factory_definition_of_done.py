import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def test_factory_has_37_engines():
    roadmap = json.loads((ROOT / "IMPLEMENTATION_ROADMAP.json").read_text())
    engines = list((ROOT / "tools/a1os_factory").rglob("*_engine.py"))
    assert roadmap["engines"] == 37
    assert len(engines) == 37

def test_factory_engines_are_deterministic_contracts():
    sys.path.insert(0, str(ROOT))
    from tools.a1os_factory.engine_runtime import make_engine
    engine = make_engine("test", "test-capability")
    one = engine.plan("demo", {"capabilities": ["test-capability"], "roles": ["owner"]})
    two = engine.plan("demo", {"capabilities": ["test-capability"], "roles": ["owner"]})
    assert one["plan_id"] == two["plan_id"]

def test_verticals_present():
    for name in ("little-oaks", "legal", "charity"):
        assert (ROOT / "products/verticals" / name).is_dir()

def test_no_jarvis_in_control_plane():
    text = (ROOT / "core/control_plane/app.py").read_text().lower()
    assert "jarvis" not in text

def test_control_plane_command_is_allowlisted():
    text = (ROOT / "core/control_plane/app.py").read_text()
    assert "ALLOWED_COMMANDS" in text
    assert '"bash"' not in text
