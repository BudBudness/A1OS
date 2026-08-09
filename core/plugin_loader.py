import importlib
from typing import Dict, List, Any

class PluginLoader:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.loaded = False
    
    def discover_plugins(self, package_path: str):
        import pkgutil
        import inspect
        for module_info in pkgutil.iter_modules([package_path]):
            module_name = module_info.name
            try:
                module = importlib.import_module(f"{package_path}.{module_name}")
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "plugin_metadata"):
                        self.plugins[name] = obj()
            except Exception as e:
                pass
    
    def get_plugin(self, name: str) -> Any:
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
