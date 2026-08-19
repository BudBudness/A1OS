from fastapi.testclient import TestClient

from core.control_plane.app import app


client = TestClient(app)


def test_status_is_read_only():
    response = client.post(
        "/api/jarvis/plan",
        json={"command": "status"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk"] == "read"
    assert data["requires_approval"] is False
    assert data["approval_token"] is None


def test_terminal_requires_human_approval():
    response = client.post(
        "/api/jarvis/plan",
        json={"command": "run echo A1OS"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk"] == "execute"
    assert data["requires_approval"] is True
    assert data["approval_token"]


def test_destructive_requires_human_approval():
    response = client.post(
        "/api/jarvis/plan",
        json={"command": "stop"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk"] == "destructive"
    assert data["requires_approval"] is True
    assert data["approval_token"]


def test_invalid_approval_token_is_rejected():
    response = client.post(
        "/api/jarvis/approve",
        json={"token": "invalid-token"},
    )
    assert response.status_code == 404
