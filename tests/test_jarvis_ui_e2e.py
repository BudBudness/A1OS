
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
    assert plan.status_code == 200
    decision = plan.json()

    assert decision["intent"] == "terminal"
    assert decision["risk"] == "execute"
    assert decision["requires_approval"] is True
    token = decision["approval_token"]
    assert token

    denied = client.post("/api/jarvis/approve", json={"approval_token": "invalid-token"})
    assert denied.status_code in (400, 404, 422)

    approved = client.post("/api/jarvis/approve", json={"token": token})
    assert approved.status_code == 200
    result = approved.json()
    assert result["status"] == "completed"
    assert result["exit_code"] == 0
    assert result["output"].strip()

    status = client.get("/api/status")
    assert status.status_code == 200
    body = status.json()
    assert body["a1os"] == "online"
    assert body["human_authority"] is True
    assert body["autonomous_execution"] == "approval_gated"
