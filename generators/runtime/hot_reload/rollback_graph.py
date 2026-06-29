import logging
import importlib
import sys

logger = logging.getLogger("A1OS-Rollback")

class VersionedRollbackGraph:
    def __init__(self):
        self.dependency_graph = {}
        self.version_store = {}

    def register_dependency(self, parent_module: str, child_module: str):
        if parent_module not in self.dependency_graph:
            self.dependency_graph[parent_module] = set()
        self.dependency_graph[parent_module].add(child_module)

    def snapshot_version(self, module_name: str, module_object):
        """Saves a reference/bytecode snapshot of a working module."""
        self.version_store[module_name] = module_object
        logger.info(f"[ROLLBACK] Version snapshotted for module: {module_name}")

    def rollback(self, failed_module: str):
        """Reverts a failed module to the last known stable snapshot."""
        if failed_module in self.version_store:
            logger.warning(f"[ROLLBACK] Reverting {failed_module} to stable version.")
            sys.modules[failed_module] = self.version_store[failed_module]
            return {"status": "ROLLED_BACK", "module": failed_module}
        else:
            logger.error(f"[ROLLBACK] No stable snapshot found for {failed_module}. Aborting rollback.")
            return {"status": "ROLLBACK_FAILED", "reason": "snapshot_not_found"}
