
from typing import Callable, Any

class WorkerPool:
    def __init__(self, pool_size: int = 4):
        self.pool_size = pool_size
        self.idle_workers = pool_size
        
    def execute(self, task_func: Callable, *args: Any, **kwargs: Any) -> Any:
        # Implementation for thread/process pool execution
        if self.idle_workers > 0:
            self.idle_workers -= 1
            try:
                return task_func(*args, **kwargs)
            finally:
                self.idle_workers += 1
        raise Exception("Worker pool exhausted")

