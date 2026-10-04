import pytest

from core.worker import _single_worker_lock

def test_worker_singleton_lock_blocks_second_instance(tmp_path, monkeypatch):
    lock_path = tmp_path / "a1os-worker.lock"
    monkeypatch.setattr("core.worker.LOCK_PATH", str(lock_path))
    with _single_worker_lock():
        with pytest.raises(SystemExit, match="A1OS worker already running"):
            with _single_worker_lock():
                pass
