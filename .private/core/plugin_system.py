import importlib, os

class PluginSystem:
    def load(self, runtime):
        for f in os.listdir("modules"):
            if f.endswith(".py"):
                mod = importlib.import_module("modules." + f[:-3])
                if hasattr(mod, "register"):
                    mod.register(runtime)
