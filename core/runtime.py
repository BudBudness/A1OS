import asyncio
from typing import Any, Dict


class Runtime:
    """
    Canonical A1OS task execution runtime.

    Routes incoming tasks to the appropriate subsystem while preserving
    the A1OS event-driven execution model.
    """

    def __init__(self, system=None):
        self.system = system
        self.started = False

    async def start(self):
        self.started = True
        print("[A1OS] Execution runtime online.")

    async def execute(self, task_id: str, payload: Dict[str, Any]):
        target = str(payload.get("target", "default")).lower()
        action = payload.get("action", "default")

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

                await system.bus.publish(
                    "task.completed",
                    {
                        "task_id": task_id,
                        "payload": result,
                    }
                )

            return result

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

            if system is not None:
                await system.bus.publish(
                    "task.failed",
                    {
                        "task_id": task_id,
                        "payload": result,
                    }
                )

            return result
