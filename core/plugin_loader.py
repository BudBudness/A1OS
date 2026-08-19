import importlib.util
import inspect
from pathlib import Path
from typing import Any, List


class PluginLoader:
    def __init__(self):
        self.loaded = False
        self.plugins = {}

    def discover_plugins(self, package_path: str):
        discovered = []
        root = Path(package_path)

        if not root.is_dir():
            self.loaded = True
            return discovered

        for module_path in sorted(root.glob("*.py")):
            if module_path.name == "__init__.py":
                continue

            module_name = f"_a1os_plugin_{module_path.stem}"
            try:
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    module_path,
                )
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except (ImportError, ModuleNotFoundError, OSError, SyntaxError):
                continue

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ != module.__name__:
                    continue
                if not hasattr(obj, "plugin_metadata"):
                    continue

                try:
                    self.plugins[name] = obj()
                except Exception:
                    continue

                discovered.append(name)

        self.loaded = True
        return discovered

    def get_plugin(self, name: str) -> Any:
        return self.plugins.get(name)

    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
