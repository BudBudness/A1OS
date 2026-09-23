from fastapi.testclient import TestClient
from core.control_plane.app import app

client = TestClient(app)

def test_status_is_read_only():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["human_authority"] is True
    assert data["execution_policy"] == "approval_gated"

def test_command_requires_human_approval():
    response = client.post("/api/command", json={"command": "git status --short"})
    assert response.status_code == 200
    data = response.json()
    assert data["approval_required"] is True
    assert data["status"] == "approval_required"

def test_command_allowlist_blocks_arbitrary_shell():
    response = client.post("/api/command", json={"command": "rm -rf /"})
    assert response.status_code == 403

def test_approved_allowlisted_command_executes():
    response = client.post("/api/command", json={"command": "git diff --check", "approve": True})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
