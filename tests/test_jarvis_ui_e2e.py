
import json
from fastapi.testclient import TestClient
from core.control_plane.app import app

client = TestClient(app)

def test_ui_to_plan_approval_execution_audit_flow():
    ui = client.get("/ui/")
    assert ui.status_code == 200
    assert "A1OS" in ui.text
    assert "JARVIS" in ui.text
    assert "Send" in ui.text

    plan = client.post("/api/jarvis/plan", json={"command": "run pwd"})
    assert plan.status_code == 410
    decision = plan.json()
    assert isinstance(decision, dict)

    denied = client.post("/api/jarvis/approve", json={"approval_token": "invalid-token"})
    assert denied.status_code in (400, 404, 422)


def test_little_oaks_vertical_resolves_through_control_plane():
    from core.control_plane.jarvis import resolve_vertical

    vertical = resolve_vertical("little-oaks")

    assert vertical["name"] == "little-oaks"
    assert vertical["runtime"] == "clients/little-oaks"
    assert vertical["backend"] == "a1os-platform-api"
    assert vertical["core"] == "a1os-core"
