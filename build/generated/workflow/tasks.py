import time

class SystemTaskRegistry:
    def __init__(self):
        self._handlers = {}
        self._register_builtins()

    def _register_builtins(self):
        self.register("DATA_RECONCILE", lambda p: print(f"[TASK-EXEC] Reconciled system state maps for payload signature: {p}"))
        self.register("TELEMETRY_SYNC", lambda p: time.sleep(0.1) or print("[TASK-EXEC] Sync block flushed to disk."))

    def register(self, name, func):
        self._handlers[name.upper()] = func

    def get_handler(self, name):
        return self._handlers.get(name.upper())