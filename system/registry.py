import importlib
class PluginRegistry:
    plugins = {}
    @classmethod
    def register(cls, name, module_path):
        cls.plugins[name] = importlib.import_module(module_path)
