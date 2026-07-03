import json, importlib, os, asyncio

class Registry:
    def __init__(self, config_path="~/A1OS/cfg/registry.json"):
        self.config_path = os.path.expanduser(config_path)
        self.providers = {}

    async def initialize(self):
        # Offload file I/O and dynamic imports to a thread to prevent blocking
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                for name, module_path in data.get("providers", {}).items():
                    try:
                        loop = asyncio.get_event_loop()
                        module = await loop.run_in_executor(None, importlib.import_module, module_path.replace('/', '.'))
                        self.providers[name] = module.Provider()
                    except Exception as e:
                        print(f"Registry Warning: {name} load error: {e}")

    def get_provider(self, name):
        return self.providers.get(name)

registry = Registry()
