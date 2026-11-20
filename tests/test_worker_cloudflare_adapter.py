import ast
from pathlib import Path

from core import queue as queue_package
from core.queue import durable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_background_worker_uses_durable_queue_facade_not_legacy_store():
    source = (REPOSITORY_ROOT / "core" / "worker.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "DurableQueue" in imports
    assert "store" not in imports
    assert "supabase_tasks" not in source
    for method in ("pending", "claim", "complete", "fail", "recover_running"):
        assert f"DurableQueue.{method}" in source


def test_cloudflare_recovery_receives_configured_stale_threshold(monkeypatch):
    captured = {}

    class FakeCloudStore:
        def recover_stale_tasks(self, stale_after_seconds=300):
            captured["stale_after_seconds"] = stale_after_seconds
            return 2

    monkeypatch.setattr(durable, "_cloud_store", lambda: FakeCloudStore())
    assert durable.DurableQueue.recover_running(stale_after_seconds=47) == 2
    assert captured["stale_after_seconds"] == 47


def test_local_recovery_applies_stale_threshold(monkeypatch):
    captured = {}

    class FakeCursor:
        rowcount = 1

    class FakeDatabase:
        @staticmethod
        def execute(sql, params=()):
            captured["sql"] = sql
            captured["params"] = params
            return FakeCursor()

    monkeypatch.setattr(durable, "_cloud_store", lambda: None)
    monkeypatch.setattr(durable, "Database", FakeDatabase)
    assert durable.DurableQueue.recover_running(stale_after_seconds=63) == 1
    assert "datetime(updated_at) < datetime('now', ? || ' seconds')" in captured["sql"]
    assert captured["params"] == ("-63",)
