def test_cloud_worker_requires_secret(monkeypatch):
    import app as api

    monkeypatch.setattr(api, "_production_cloud_store", lambda: True)
    monkeypatch.setenv("A1OS_WORKER_SECRET", "worker-secret")

    response = api.app.test_client().post("/v1/worker/run", json={"limit": 1})
    assert response.status_code == 401
    assert response.get_json()["detail"] == "Worker authentication failed"


def test_cloud_worker_rejects_invalid_limit_body(monkeypatch):
    import app as api

    monkeypatch.setattr(api, "_production_cloud_store", lambda: True)
    monkeypatch.setenv("A1OS_WORKER_SECRET", "worker-secret")

    response = api.app.test_client().post(
        "/v1/worker/run",
        headers={"X-A1OS-Worker-Token": "worker-secret"},
        json=["not", "an", "object"],
    )
    assert response.status_code == 422
    assert response.get_json()["detail"] == "JSON object body required"
