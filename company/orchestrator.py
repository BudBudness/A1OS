from company.registry import Registry

class Orchestrator:
    def __init__(self):
        self.registry = Registry()
        # Initialize registry with workers
        self._bootstrap_workers()

    def _bootstrap_workers(self):
        # Auto-register available workers from the registry
        pass
