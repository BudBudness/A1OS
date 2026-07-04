class Department:
    def __init__(self, name, manager):
        self.name = name
        self.manager = manager
        self.workers = []

    def receive_task(self, task):
        # Validate against governance policies before dispatching to worker
        raise NotImplementedError("Implementation required")
