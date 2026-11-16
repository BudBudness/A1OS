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

    monkeypatch.setattr(worker.supabase_tasks, "recover_stale_tasks", lambda stale: 0)
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

    monkeypatch.setattr(worker.supabase_tasks, "recover_stale_tasks", lambda stale: 0)
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


async def test_worker_records_execution_exception_in_supabase(monkeypatch):
    lifecycle = []
    monkeypatch.setattr(worker.supabase_tasks, "recover_stale_tasks", lambda stale: 0)
    monkeypatch.setattr(worker.supabase_tasks, "pending_tasks", lambda limit: [_task()])
    monkeypatch.setattr(worker.supabase_tasks, "claim_task", lambda task_id: True)
    monkeypatch.setattr(
        worker.supabase_tasks,
        "fail_task",
        lambda task_id, error: lifecycle.append((task_id, error)),
    )

    async def fail_execution(task_id, payload):
        raise RuntimeError("execution unavailable")

    monkeypatch.setattr(worker, "_execute_payload", fail_execution)

    assert await worker.process_once() == 1
    assert lifecycle == [("cloud-task-1", "execution unavailable")]


async def test_worker_recovers_stale_tasks_before_listing_pending(monkeypatch):
    calls = []
    monkeypatch.setattr(
        worker.supabase_tasks,
        "recover_stale_tasks",
        lambda stale: calls.append(("recover", stale)) or 0,
    )
    monkeypatch.setattr(
        worker.supabase_tasks,
        "pending_tasks",
        lambda limit: calls.append(("pending", limit)) or [],
    )

    assert await worker.process_once(limit=2) == 0
    assert calls == [
        ("recover", worker.STALE_SECONDS),
        ("pending", 2),
    ]


async def test_worker_does_not_execute_task_when_atomic_claim_is_lost(monkeypatch):
    monkeypatch.setattr(worker.supabase_tasks, "recover_stale_tasks", lambda stale: 0)
    monkeypatch.setattr(worker.supabase_tasks, "pending_tasks", lambda limit: [_task()])
    monkeypatch.setattr(worker.supabase_tasks, "claim_task", lambda task_id: False)

    async def unexpected_execution(*args, **kwargs):
        raise AssertionError("unclaimed task must not execute")

    monkeypatch.setattr(worker, "_execute_payload", unexpected_execution)

    assert await worker.process_once() == 0


async def test_worker_requeues_task_when_execution_is_cancelled(monkeypatch):
    import asyncio
    import pytest

    lifecycle = []
    monkeypatch.setattr(worker.supabase_tasks, "recover_stale_tasks", lambda stale: 0)
    monkeypatch.setattr(worker.supabase_tasks, "pending_tasks", lambda limit: [_task()])
    monkeypatch.setattr(worker.supabase_tasks, "claim_task", lambda task_id: True)
    monkeypatch.setattr(
        worker.supabase_tasks,
        "fail_task",
        lambda task_id, error: lifecycle.append((task_id, error)),
    )

    async def cancel_execution(task_id, payload):
        raise asyncio.CancelledError

    monkeypatch.setattr(worker, "_execute_payload", cancel_execution)

    with pytest.raises(asyncio.CancelledError):
        await worker.process_once()

    assert lifecycle == [
        ("cloud-task-1", "Worker cancelled during task execution"),
    ]


async def test_worker_exits_cleanly_when_shutdown_is_requested(tmp_path, monkeypatch):
    import asyncio

    stop_event = asyncio.Event()
    calls = []
    monkeypatch.setattr(worker, "LOCK_PATH", str(tmp_path / "worker.lock"))

    async def finish_current_batch():
        calls.append("finished")
        stop_event.set()

    monkeypatch.setattr(worker, "process_once", finish_current_batch)

    await worker.run_worker(stop_event)
    assert calls == ["finished"]


async def test_runtime_does_not_touch_local_queue_for_already_claimed_cloud_task(monkeypatch):
    from types import SimpleNamespace

    from core.queue.durable import DurableQueue
    from core.runtime import Runtime

    async def execute(action, **kwargs):
        return {"action": action, "ok": True}

    async def publish(*args, **kwargs):
        return None

    system = SimpleNamespace(
        finance=SimpleNamespace(execute=execute),
        bus=SimpleNamespace(publish=publish),
    )
    runtime = Runtime(system=system)

    def unexpected_queue_access(*args, **kwargs):
        raise AssertionError("cloud execution must not access the local queue")

    monkeypatch.setattr(DurableQueue, "claim", unexpected_queue_access)
    monkeypatch.setattr(DurableQueue, "complete", unexpected_queue_access)
    monkeypatch.setattr(DurableQueue, "fail", unexpected_queue_access)

    result = await runtime.execute(
        task_id="cloud-task-1",
        payload={"target": "finance", "role": "system", "action": "health_check"},
        already_claimed=True,
        manage_queue=False,
    )

    assert result["status"] == "completed"
    assert result["result"] == {"action": "health_check", "ok": True}


async def test_runtime_does_not_retry_cloud_failure_in_local_queue(monkeypatch):
    from types import SimpleNamespace

    from core.queue.durable import DurableQueue
    from core.runtime import Runtime

    async def execute(action, **kwargs):
        raise RuntimeError("simulated execution failure")

    async def publish(*args, **kwargs):
        return None

    system = SimpleNamespace(
        finance=SimpleNamespace(execute=execute),
        bus=SimpleNamespace(publish=publish),
    )
    runtime = Runtime(system=system)

    def unexpected_queue_access(*args, **kwargs):
        raise AssertionError("cloud execution must not access the local queue")

    monkeypatch.setattr(DurableQueue, "claim", unexpected_queue_access)
    monkeypatch.setattr(DurableQueue, "complete", unexpected_queue_access)
    monkeypatch.setattr(DurableQueue, "fail", unexpected_queue_access)

    result = await runtime.execute(
        task_id="cloud-task-2",
        payload={"target": "finance", "role": "system", "action": "health_check"},
        already_claimed=True,
        manage_queue=False,
    )

    assert result["status"] == "failed"
    assert result["error"] == "simulated execution failure"
