import asyncio
from typing import Any, Dict
from core.queue.durable import DurableQueue


class Runtime:
    """
    Canonical A1OS task execution runtime.

    Routes incoming tasks to the appropriate subsystem while preserving
    the A1OS event-driven execution model.
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
        print("[A1OS] Durable task worker online.")

    async def _durable_worker(self):
        while self.worker_running:
            try:
                pending = DurableQueue.pending(limit=10)

                for row in pending:
                    task_id = row["task_id"]

                    if row["status"] not in {"queued", "retry"}:
                        continue

                    payload = {
                        "target": row["target"],
                        "role": row["role"],
                        "action": row["action"],
                    }

                    import json
                    payload["data"] = json.loads(row["payload"])

                    await self.execute(
                        task_id=task_id,
                        payload=payload,
                    )

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
                engine = getattr(system, target, None)

                if engine is not None:
                    execute_method = getattr(engine, "execute", None)

                    if execute_method:
                        output = execute_method(
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
                    }
                )

            return result
