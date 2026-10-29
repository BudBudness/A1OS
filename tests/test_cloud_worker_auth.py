def test_cloud_worker_requires_secret(monkeypatch):
    import app as api

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("A1OS_WORKER_SECRET", "worker-secret")
    monkeypatch.setattr(api.supabase_tasks, "url", "https://example.supabase.co")
    monkeypatch.setattr(api.supabase_tasks, "key", "test-key")

    response = api.app.test_client().post("/v1/worker/run", json={"limit": 1})
    assert response.status_code == 401
    assert response.get_json()["detail"] == "Worker authentication failed"


def test_cloud_worker_rejects_invalid_limit_body(monkeypatch):
    import app as api

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("A1OS_WORKER_SECRET", "worker-secret")
    monkeypatch.setattr(api.supabase_tasks, "url", "https://example.supabase.co")
    monkeypatch.setattr(api.supabase_tasks, "key", "test-key")

    response = api.app.test_client().post(
        "/v1/worker/run",
        headers={"X-A1OS-Worker-Token": "worker-secret"},
        json=["not", "an", "object"],
    )
    assert response.status_code == 422
    assert response.get_json()["detail"] == "JSON object body required"


def test_vercel_cron_runs_bounded_batch_with_bearer_secret(monkeypatch):
    import app as api
    from core import worker

    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("CRON_SECRET", "cron-secret")
    monkeypatch.setattr(api.supabase_tasks, "url", "https://example.supabase.co")
    monkeypatch.setattr(api.supabase_tasks, "key", "test-key")
    calls = []

    async def fake_process_once(limit):
        calls.append(limit)
        return 2

    monkeypatch.setattr(worker, "process_once", fake_process_once)

    response = api.app.test_client().get(
        "/v1/worker/run",
        headers={"Authorization": "Bearer cron-secret"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"status": "processed", "count": 2}
    assert calls == [3]
