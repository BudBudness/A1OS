import importlib
import logging
from pathlib import Path

class PluginLoader:
    def __init__(self, registry_path=None):
        self.logger = logging.getLogger("A1OS.PluginLoader")
        self.registry_path = Path(registry_path or Path(__file__).parent)

    def load_plugins(self, runtime):
        for plugin in self.registry_path.glob("*.py"):
            if plugin.stem in ("__init__", "loader", "core", "registry"):
                continue
            module_name = f"marketplace.registry.{plugin.stem}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "register"):
                    module.register(runtime)
                    self.logger.info("Loaded plugin %s", plugin.stem)
            except Exception as exc:
                self.logger.exception("Failed loading %s: %s", plugin.stem, exc)
