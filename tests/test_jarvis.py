from fastapi.testclient import TestClient

from core.control_plane.app import app


client = TestClient(app)


def test_jarvis_status_plan():
    response = client.post(
        "/api/jarvis/plan",
        json={"command": "status"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "status"
    assert data["requires_approval"] is False


def test_jarvis_terminal_requires_approval():
    response = client.post(
        "/api/jarvis/plan",
        json={"command": "run echo A1OS"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "terminal"
    assert data["requires_approval"] is True


def test_jarvis_unknown_does_not_execute():
    response = client.post(
        "/api/jarvis/plan",
        json={"command": "do something"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "unknown"
    assert data["command"] is None
