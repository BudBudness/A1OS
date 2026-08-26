import asyncio
import importlib
import inspect
import logging
from pathlib import Path
from threading import Thread


class PluginLoader:
    def __init__(self, registry_path=None):
        self.logger = logging.getLogger("A1OS.PluginLoader")
        self.registry_path = Path(registry_path or Path(__file__).parent)

    @staticmethod
    def _run_awaitable(result):
        if not inspect.isawaitable(result):
            return result

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(result)

        # Preserve the historical synchronous loader contract even when
        # called from an already-running event loop.
        state = {"result": None, "error": None}

        def runner():
            try:
                state["result"] = asyncio.run(result)
            except BaseException as exc:
                state["error"] = exc

        thread = Thread(target=runner, daemon=True)
        thread.start()
        thread.join()

        if state["error"] is not None:
            raise state["error"]

        return state["result"]

    def load_plugins(self, runtime):
        for plugin in self.registry_path.glob("*.py"):
            if plugin.stem in ("__init__", "loader", "core", "registry"):
                continue

            module_name = f"marketplace.registry.{plugin.stem}"

            try:
                module = importlib.import_module(module_name)

                if hasattr(module, "register"):
                    result = module.register(runtime)
                    self._run_awaitable(result)
                    self.logger.info("Loaded plugin %s", plugin.stem)

            except Exception as exc:
                self.logger.exception(
                    "Failed loading %s: %s",
                    plugin.stem,
                    exc,
                )
