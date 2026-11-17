"""Exercise the remote queue acceptance probe without credentials or network access."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_cloudflare_queue_e2e.py"
spec = importlib.util.spec_from_file_location("a1os_queue_acceptance", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_missing_credentials_fail_closed(monkeypatch):
    monkeypatch.delenv("A1OS_TASK_QUEUE_URL", raising=False)
    monkeypatch.delenv("A1OS_TASK_QUEUE_TOKEN", raising=False)
    assert probe.main() == 2


def test_remote_lifecycle_requires_persisted_completion(monkeypatch):
    monkeypatch.setenv("A1OS_TASK_QUEUE_URL", "https://example.invalid")
    monkeypatch.setenv("A1OS_TASK_QUEUE_TOKEN", "test-only")
    class FakeStore:
        def __init__(self, **kwargs):
            self.state = "absent"
        def enqueue(self, target, role, action, data, task_id=None):
            assert (target, role, action) == ("staging", "smoke", "noop")
            self.task_id = task_id
            self.state = "queued"
            return task_id
        def get_task(self, task_id):
            assert task_id == self.task_id
            return {"status": self.state}
        def claim_task(self, task_id):
            if self.state != "queued":
                return False
            self.state = "running"
            return True
        def complete_task(self, task_id):
            self.state = "completed"
    with patch.object(probe, "CloudflareTaskStore", FakeStore):
        assert probe.main() == 0


def test_remote_lifecycle_rejects_false_completion(monkeypatch):
    monkeypatch.setenv("A1OS_TASK_QUEUE_URL", "https://example.invalid")
    monkeypatch.setenv("A1OS_TASK_QUEUE_TOKEN", "test-only")
    class FakeStore:
        def __init__(self, **kwargs):
            self.state = "queued"
        def enqueue(self, target, role, action, data, task_id=None):
            return task_id
        def get_task(self, task_id):
            return {"status": self.state}
        def claim_task(self, task_id):
            if self.state == "queued":
                self.state = "running"
                return True
            return False
        def complete_task(self, task_id):
            pass
    with patch.object(probe, "CloudflareTaskStore", FakeStore):
        assert probe.main() == 1
