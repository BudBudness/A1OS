from core import worker


def _task():
    return {
        "task_id": "cloud-task-1",
        "target": "finance",
        "role": "system",
        "action": "health_check",
        "payload": {},
        "status": "queued",
    }


async def test_worker_executes_claimed_cloud_task_without_reclaiming_or_local_enqueue(monkeypatch):
    lifecycle = []
    runtime_calls = []

    monkeypatch.setattr(worker.supabase_tasks, "pending_tasks", lambda limit: [_task()])
    monkeypatch.setattr(
        worker.supabase_tasks,
        "claim_task",
        lambda task_id: lifecycle.append(("claim", task_id)) or True,
    )
    monkeypatch.setattr(
        worker.supabase_tasks,
        "complete_task",
        lambda task_id: lifecycle.append(("complete", task_id)),
    )
    monkeypatch.setattr(
        worker.supabase_tasks,
        "fail_task",
        lambda task_id, error: lifecycle.append(("fail", task_id, error)),
    )

    async def fake_runtime_execute(**kwargs):
        runtime_calls.append(kwargs)
        return {"task_id": kwargs["task_id"], "status": "completed"}

    monkeypatch.setattr(worker.system.runtime, "execute", fake_runtime_execute)

    processed = await worker.process_once()

    assert processed == 1
    assert lifecycle == [
        ("claim", "cloud-task-1"),
        ("complete", "cloud-task-1"),
    ]
    assert len(runtime_calls) == 1
    assert runtime_calls[0]["task_id"] == "cloud-task-1"
    assert runtime_calls[0]["already_claimed"] is True
    assert runtime_calls[0]["manage_queue"] is False


async def test_worker_records_runtime_failure_in_supabase(monkeypatch):
    lifecycle = []

    monkeypatch.setattr(worker.supabase_tasks, "pending_tasks", lambda limit: [_task()])
    monkeypatch.setattr(worker.supabase_tasks, "claim_task", lambda task_id: True)
    monkeypatch.setattr(
        worker.supabase_tasks,
        "complete_task",
        lambda task_id: lifecycle.append(("complete", task_id)),
    )
    monkeypatch.setattr(
        worker.supabase_tasks,
        "fail_task",
        lambda task_id, error: lifecycle.append(("fail", task_id, error)),
    )

    async def fake_runtime_execute(**kwargs):
        return {"task_id": kwargs["task_id"], "status": "failed", "error": "test failure"}

    monkeypatch.setattr(worker.system.runtime, "execute", fake_runtime_execute)

    processed = await worker.process_once()

    assert processed == 1
    assert lifecycle == [("fail", "cloud-task-1", "test failure")]
