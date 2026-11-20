import httpx

from core.persistence.cloudflare_tasks import CloudflareTaskStore
from core.queue.durable import _cloud_store


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("request failed", request=None, response=None)

    def json(self):
        return self._payload


def test_enqueue_uses_authenticated_worker_api(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        httpx,
        "request",
        lambda method, url, **kwargs: (
            captured.update(method=method, url=url, **kwargs) or FakeResponse({"task_id": "t-1"})
        ),
    )
    store = CloudflareTaskStore("https://queue.example.workers.dev", "token")
    assert store.enqueue("research", "analyst", "scan", {"symbol": "BTC"}, "t-1") == "t-1"
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/v1/tasks")
    assert captured["headers"]["Authorization"] == "Bearer token"
    assert captured["json"]["task_id"] == "t-1"


def test_claim_conflict_means_task_was_not_claimed(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: FakeResponse({}, 409))
    store = CloudflareTaskStore("https://queue.example.workers.dev", "token")
    assert store.claim_task("t-1") is False


def test_claim_success_returns_worker_claim_flag(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: FakeResponse({"claimed": True}))
    store = CloudflareTaskStore("https://queue.example.workers.dev", "token")
    assert store.claim_task("t-1") is True


def test_pending_tasks_reads_worker_data(monkeypatch):
    monkeypatch.setattr(
        httpx,
        "request",
        lambda *args, **kwargs: FakeResponse({"data": [{"task_id": "t-1"}]}),
    )
    store = CloudflareTaskStore("https://queue.example.workers.dev", "token")
    assert store.pending_tasks(10) == [{"task_id": "t-1"}]


def test_cloud_store_uses_configured_cloudflare_endpoint(monkeypatch):
    monkeypatch.setenv("A1OS_TASK_QUEUE_URL", "https://queue.example.workers.dev")
    monkeypatch.setenv("A1OS_TASK_QUEUE_TOKEN", "token")
    store = _cloud_store()
    assert isinstance(store, CloudflareTaskStore)
    assert store.configured


def test_local_runtime_uses_local_queue_when_cloudflare_is_unconfigured(monkeypatch):
    monkeypatch.delenv("A1OS_TASK_QUEUE_URL", raising=False)
    monkeypatch.delenv("A1OS_TASK_QUEUE_TOKEN", raising=False)
    assert _cloud_store() is None

def test_remote_queue_requires_url_and_token_together(monkeypatch):
    monkeypatch.setenv("A1OS_TASK_QUEUE_URL", "https://queue.example.workers.dev")
    monkeypatch.delenv("A1OS_TASK_QUEUE_TOKEN", raising=False)
    try:
        _cloud_store()
    except RuntimeError as error:
        assert "must be configured together" in str(error)
    else:
        raise AssertionError("partial queue configuration must fail closed")
