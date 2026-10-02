import asyncio
import json
import os
from typing import Any

from core.persistence.supabase_tasks import store as supabase_tasks
from core.queue.durable import DurableQueue
from core.state import system


POLL_SECONDS = float(os.environ.get("A1OS_WORKER_POLL_SECONDS", "2"))
BATCH_SIZE = int(os.environ.get("A1OS_WORKER_BATCH_SIZE", "10"))


def _row_payload(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload") or {}
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        payload = {}
    return {
        "target": row["target"],
        "role": row["role"],
        "action": row["action"],
        **payload,
    }


async def _execute_payload(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    target = str(payload["target"]).lower()
    action = str(payload["action"])

    if target == "a1os":
        output = await system.execute(
            action,
            **{
                key: value
                for key, value in payload.items()
                if key not in {"target", "role", "action"}
            },
        )
        DurableQueue.complete(task_id)
        return {"task_id": task_id, "status": "completed", "result": output}

    return await system.runtime.execute(task_id=task_id, payload=payload)


async def process_once() -> int:
    rows = supabase_tasks.pending_tasks(limit=BATCH_SIZE)
    processed = 0

    for row in rows:
        task_id = str(row["task_id"])
        if not supabase_tasks.claim_task(task_id):
            continue

        payload = _row_payload(row)

        try:
            DurableQueue.enqueue(
                target=payload["target"],
                role=payload["role"],
                action=payload["action"],
                data={
                    key: value
                    for key, value in payload.items()
                    if key not in {"target", "role", "action"}
                },
                task_id=task_id,
            )
            result = await _execute_payload(task_id, payload)

            if result.get("status") == "completed":
                supabase_tasks.complete_task(task_id)
            else:
                supabase_tasks.fail_task(
                    task_id,
                    result.get("error", "Task execution failed"),
                )

        except Exception as exc:
            supabase_tasks.fail_task(task_id, str(exc))

        processed += 1

    return processed


async def run_worker() -> None:
    print("[A1OS] Supabase worker online.")

    while True:
        try:
            await process_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"[A1OS] Supabase worker error: {type(exc).__name__}: {exc}")
        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(run_worker())
