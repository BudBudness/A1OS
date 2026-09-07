class WorkerRegistry:
    def __init__(self):
        self._workers = {}

    def register(self, name, worker):
        if not name:
            raise ValueError("worker name is required")
        if worker is None:
            raise ValueError("worker is required")
        self._workers[name] = worker
        return worker

    def get(self, name):
        return self._workers.get(name)

    def names(self):
        return tuple(sorted(self._workers))

    def snapshot(self):
        return dict(self._workers)
