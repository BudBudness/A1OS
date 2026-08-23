from fastapi.testclient import TestClient

from core.control_plane.app import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["human_authority"] is True


def test_command_requires_approval():
    response = client.post("/api/command", json={"command": "printf control-plane"})
    assert response.status_code == 200
    assert response.json()["approval_required"] is True


def test_approved_command():
    response = client.post(
        "/api/command",
        json={"command": "printf control-plane", "approve": True},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["output"] == "control-plane"


def test_dangerous_command_blocked():
    response = client.post(
        "/api/command",
        json={"command": "rm -rf /", "approve": True},
    )
    assert response.status_code == 403
