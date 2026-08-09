import asyncio
from typing import Any, Dict

from core.queue.durable import DurableQueue


class Runtime:
    """
    Canonical A1OS task execution runtime.

    Responsibilities:
    - Claim durable tasks atomically.
    - Execute tasks through the registered system engine.
    - Complete successful tasks.
    - Retry failed tasks through DurableQueue.fail().
    - Publish task lifecycle events.
    - Run a durable background worker.
    """

    def __init__(self, system=None):
        self.system = system
        self.started = False
        self.worker_task = None
        self.worker_running = False

    async def start(self):
        self.started = True
        self.worker_running = True
        self.worker_task = asyncio.create_task(self._durable_worker())
        print("[A1OS] Execution runtime online.")

    async def _durable_worker(self):
        while self.worker_running:
            try:
                pending = DurableQueue.pending(limit=10)

                for row in pending:
                    task_id = row["task_id"]

                    payload = {
                        "target": row["target"],
                        "role": row["role"],
                        "action": row["action"],
                    }

                    try:
                        data = row["payload"]

                        if isinstance(data, dict):
                            payload.update(data)

                    except Exception:
                        pass

                    await self.execute(task_id, payload)

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break

            except Exception as exc:
                print(f"[A1OS] Durable worker error: {exc}")
                await asyncio.sleep(2)

    async def execute(self, task_id: str, payload: Dict[str, Any]):
        target = str(payload.get("target", "default")).lower()
        action = payload.get("action", "default")

        claimed = DurableQueue.claim(task_id)

        if not claimed:
            return {
                "task_id": task_id,
                "target": target,
                "action": action,
                "status": "skipped",
                "reason": "task_already_claimed_or_not_pending",
            }

        result = {
            "task_id": task_id,
            "target": target,
            "action": action,
            "status": "completed",
        }

        system = self.system

        try:
            if system is not None:
                if target == "system":
                    output = system.execute(
                        action,
                        **{
                            k: v
                            for k, v in payload.items()
                            if k not in {"target", "action", "role"}
                        }
                    )

                    if asyncio.iscoroutine(output):
                        output = await output

                    result["result"] = output
                    DurableQueue.complete(task_id)

                    await system.bus.publish(
                        "task.completed",
                        {
                            "task_id": task_id,
                            "payload": result,
                        }
                    )

                    return result

                engine = getattr(system, target, None)

                if engine is None:
                    raise RuntimeError(
                        f"No execution engine registered for target: {target}"
                    )

                execute_method = getattr(engine, "execute", None)

                if execute_method is None:
                    raise RuntimeError(
                        f"Execution engine for target '{target}' "
                        "has no execute method"
                    )

                output = execute_method(
                    action,
                    **{
                        key: value
                        for key, value in payload.items()
                        if key not in {"target", "action", "role"}
                    },
                )

                if asyncio.iscoroutine(output):
                    output = await output

                result["result"] = output

                DurableQueue.complete(task_id)

                await system.bus.publish(
                    "task.completed",
                    {
                        "task_id": task_id,
                        "payload": result,
                    },
                )

            else:
                DurableQueue.complete(task_id)

            return result

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

            DurableQueue.fail(task_id, exc)

            if system is not None:
                await system.bus.publish(
                    "task.failed",
                    {
                        "task_id": task_id,
                        "payload": result,
                    },
                )

            return result
