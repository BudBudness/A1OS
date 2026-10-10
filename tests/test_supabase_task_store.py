from datetime import datetime

import httpx

from core.persistence.supabase_tasks import SupabaseTaskStore


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def configured_store():
    store = SupabaseTaskStore()
    store.url = "https://example.supabase.co"
    store.key = "test-key"
    return store


def test_claim_uses_atomic_postgres_rpc(monkeypatch):
    store = configured_store()
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse([{"task_id": "t1", "status": "running", "attempts": 1}])

    monkeypatch.setattr(httpx, "post", fake_post)
    assert store.claim_task("t1") is True
    assert captured["url"].endswith("/rest/v1/rpc/a1os_claim_task")
    assert captured["json"] == {"p_task_id": "t1"}


def test_claim_returns_false_when_rpc_claims_nothing(monkeypatch):
    store = configured_store()
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: FakeResponse([]))
    assert store.claim_task("already-running") is False


def test_stale_running_task_is_recovered_only_when_update_changed_row(monkeypatch):
    store = configured_store()
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: FakeResponse([
            {"task_id": "t1", "attempts": 1, "max_attempts": 3}
        ]),
    )
    captured = {}

    def fake_patch(*args, **kwargs):
        captured.update(kwargs)
        return FakeResponse([{"task_id": "t1", "status": "retry"}])

    monkeypatch.setattr(httpx, "patch", fake_patch)
    assert store.recover_stale_tasks(stale_after_seconds=1) == 1
    assert captured["params"]["status"] == "eq.running"
    assert captured["json"]["status"] == "retry"
    assert captured["json"]["next_attempt_at"] is not None


def test_stale_task_at_max_attempts_is_terminal(monkeypatch):
    store = configured_store()
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: FakeResponse([
            {"task_id": "t1", "attempts": 3, "max_attempts": 3}
        ]),
    )
    captured = {}

    def fake_patch(*args, **kwargs):
        captured.update(kwargs)
        return FakeResponse([{"task_id": "t1", "status": "failed"}])

    monkeypatch.setattr(httpx, "patch", fake_patch)
    assert store.recover_stale_tasks(stale_after_seconds=1) == 1
    assert captured["json"]["status"] == "failed"
    assert captured["json"]["next_attempt_at"] is None


def test_approval_denial_is_terminal_in_cloud_store(monkeypatch):
    store = configured_store()
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: FakeResponse([
            {"task_id": "t1", "status": "running", "attempts": 1, "max_attempts": 3}
        ]),
    )
    captured = {}

    def fake_patch(*args, **kwargs):
        captured.update(kwargs)
        return FakeResponse([])

    monkeypatch.setattr(httpx, "patch", fake_patch)
    store.fail_task("t1", "ApprovalDenied: explicit approval required")
    assert captured["json"]["status"] == "failed"
    assert captured["json"]["next_attempt_at"] is None


def test_pending_tasks_excludes_future_retry(monkeypatch):
    store = configured_store()
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *args, **kwargs: FakeResponse([
            {"task_id": "ready", "status": "queued", "next_attempt_at": None},
            {"task_id": "later", "status": "retry", "next_attempt_at": "2999-01-01T00:00:00+00:00"},
        ]),
    )
    rows = store.pending_tasks()
    assert [row["task_id"] for row in rows] == ["ready"]
