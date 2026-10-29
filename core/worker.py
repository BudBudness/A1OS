import asyncio
import fcntl
import json
import os
import signal
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from core.persistence.supabase_tasks import store as supabase_tasks
from core.state import system

POLL_SECONDS = float(os.environ.get("A1OS_WORKER_POLL_SECONDS", "2"))
BATCH_SIZE = int(os.environ.get("A1OS_WORKER_BATCH_SIZE", "10"))
STALE_SECONDS = int(os.environ.get("A1OS_WORKER_STALE_SECONDS", "300"))
LOCK_PATH = os.path.expanduser(os.environ.get("A1OS_WORKER_LOCK_PATH", "~/.a1os-worker.lock"))

def _log(event: str, **fields: Any) -> None:
    print(json.dumps({"service": "a1os-worker", "event": event, **fields}, sort_keys=True), flush=True)

@contextmanager
def _single_worker_lock() -> Iterator[None]:
    path = Path(LOCK_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise SystemExit("A1OS worker already running")
    try:
        handle.seek(0)
        handle.truncate()
        handle.write(str(os.getpid()))
        handle.flush()
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()

def _row_payload(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload") or {}
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        payload = {}
    return {"target": row["target"], "role": row["role"], "action": row["action"], **payload}

async def _execute_payload(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    target = str(payload["target"]).lower()
    action = str(payload["action"])
    if target == "a1os":
        output = await system.execute(
            action,
            **{key: value for key, value in payload.items() if key not in {"target", "role", "action"}},
        )
        return {"task_id": task_id, "status": "completed", "result": output}
    return await system.runtime.execute(
        task_id=task_id,
        payload=payload,
        already_claimed=True,
        manage_queue=False,
    )

async def process_once(limit: int | None = None) -> int:
    batch_limit = BATCH_SIZE if limit is None else max(1, min(int(limit), 5))
    recovered = supabase_tasks.recover_stale_tasks(STALE_SECONDS)
    if recovered:
        _log("stale_tasks_recovered", count=recovered)
    rows = supabase_tasks.pending_tasks(limit=batch_limit)
    processed = 0
    for row in rows:
        task_id = str(row["task_id"])
        if not supabase_tasks.claim_task(task_id):
            continue
        payload = _row_payload(row)
        try:
            result = await _execute_payload(task_id, payload)
            if result.get("status") == "completed":
                supabase_tasks.complete_task(task_id)
            else:
                supabase_tasks.fail_task(task_id, result.get("error", "Task execution failed"))
        except asyncio.CancelledError:
            try:
                supabase_tasks.fail_task(task_id, "Worker cancelled during task execution")
            except Exception as exc:
                _log(
                    "task_cancellation_record_failed",
                    task_id=task_id,
                    error_type=type(exc).__name__,
                    error=str(exc)[:500],
                )
            raise
        except Exception as exc:
            _log("task_failed", task_id=task_id, error_type=type(exc).__name__, error=str(exc)[:500])
            supabase_tasks.fail_task(task_id, str(exc))
        processed += 1
    if processed:
        _log("batch_processed", processed=processed)
    return processed

async def run_worker(stop_event: asyncio.Event | None = None) -> None:
    stop_event = stop_event or asyncio.Event()
    with _single_worker_lock():
        _log("worker_online", poll_seconds=POLL_SECONDS, batch_size=BATCH_SIZE, stale_seconds=STALE_SECONDS)
        while not stop_event.is_set():
            try:
                await process_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log("worker_loop_error", error_type=type(exc).__name__, error=str(exc)[:500])
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=POLL_SECONDS)
            except asyncio.TimeoutError:
                pass

if __name__ == "__main__":
    async def _run_until_signal() -> None:
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        for handled_signal in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(handled_signal, stop_event.set)
        try:
            await run_worker(stop_event)
        finally:
            for handled_signal in (signal.SIGINT, signal.SIGTERM):
                loop.remove_signal_handler(handled_signal)

    asyncio.run(_run_until_signal())
