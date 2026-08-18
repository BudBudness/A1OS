class RollbackEngine:
    def __init__(self, state=None):
        self.state = state

    async def revert(self, task_id: str):
        if not task_id:
            raise ValueError("task_id is required")

        if self.state is not None:
            for name in ("rollback", "revert", "mark_failed"):
                method = getattr(self.state, name, None)
                if callable(method):
                    result = method(task_id)
                    if hasattr(result, "__await__"):
                        result = await result
                    return result

        return {
            "task_id": task_id,
            "status": "rollback_requested",
        }

    async def handle_node_failure(self, node_id: str, active_tasks: list):
        if not node_id:
            raise ValueError("node_id is required")

        results = []
        for task_id in active_tasks or []:
            results.append(await self.revert(task_id))

        return {
            "node_id": node_id,
            "status": "rollback_completed",
            "tasks": results,
        }
