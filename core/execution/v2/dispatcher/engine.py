import asyncio, json
from core.execution.v2.transport.rpc import SecureTransport
class DistributedDispatcher:
    def __init__(self):
        self._handlers = {}

    def register(self, name, handler):
        self._handlers[name] = handler
        return handler

    def dispatch(self, task, context=None):
        context = context or {}
        role = context.get("role", "user")

        if role not in {"user", "system", "admin"}:
            raise PermissionError(f"Role not authorized: {role}")

        action = task.get("action")
        handler = self._handlers.get(action)

        if handler is None:
            raise KeyError(f"Handler not found: {action}")

        result = handler(task.get("data", {}))

        if hasattr(result, "__await__"):
            import asyncio
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(result)
            return result

        return result

class DispatcherEngine:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def dispatch(self, *args, **kwargs):
        return {
            "status": "dispatched",
            "args": args,
            "kwargs": kwargs,
        }
