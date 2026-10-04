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

def test_claim_task_is_compare_and_swap(monkeypatch):
    store = SupabaseTaskStore()
    store.url = "https://example.supabase.co"
    store.key = "test-key"
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse([{"task_id": "t1", "status": "queued", "attempts": 0}]))
    captured = {}
    def fake_patch(*args, **kwargs):
        captured.update(kwargs)
        return FakeResponse([{"task_id": "t1", "status": "running", "attempts": 1}])
    monkeypatch.setattr(httpx, "patch", fake_patch)
    assert store.claim_task("t1") is True
    assert captured["params"]["status"] == "eq.queued"
    assert captured["json"]["status"] == "running"
    assert captured["json"]["attempts"] == 1
    datetime.fromisoformat(captured["json"]["updated_at"])

def test_stale_running_task_is_recovered(monkeypatch):
    store = SupabaseTaskStore()
    store.url = "https://example.supabase.co"
    store.key = "test-key"
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse([{"task_id": "t1", "attempts": 1, "max_attempts": 3}]))
    captured = {}
    def fake_patch(*args, **kwargs):
        captured.update(kwargs)
        return FakeResponse([])
    monkeypatch.setattr(httpx, "patch", fake_patch)
    assert store.recover_stale_tasks(stale_after_seconds=1) == 1
    assert captured["params"]["status"] == "eq.running"
    assert captured["json"]["status"] == "retry"
    assert captured["json"]["next_attempt_at"] is not None

def test_stale_task_at_max_attempts_is_terminal(monkeypatch):
    store = SupabaseTaskStore()
    store.url = "https://example.supabase.co"
    store.key = "test-key"
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse([{"task_id": "t1", "attempts": 3, "max_attempts": 3}]))
    captured = {}
    def fake_patch(*args, **kwargs):
        captured.update(kwargs)
        return FakeResponse([])
    monkeypatch.setattr(httpx, "patch", fake_patch)
    assert store.recover_stale_tasks(stale_after_seconds=1) == 1
    assert captured["json"]["status"] == "failed"
    assert captured["json"]["next_attempt_at"] is None
