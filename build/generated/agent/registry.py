class SovereignToolRegistry:
    def __init__(self):
        self._registry = {}
        self._load_builtins()

    def _load_builtins(self):
        self.register_tool("PING", lambda p: "PONG")
        self.register_tool("ECHO", lambda p: p.get("msg", ""))

    def register_tool(self, name, func):
        self._registry[name.upper()] = func
        print(f"[AGENT-REGISTRY] Attached executable hook vector: '{name.upper()}'")

    def get_tool(self, name):
        return self._registry.get(name.upper())