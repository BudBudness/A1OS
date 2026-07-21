
class ResourceScheduler:
    def __init__(self, cpu_limit: int, mem_limit: int):
        self.cpu = cpu_limit
        self.mem = mem_limit
        
    def allocate(self, requirements: dict) -> bool:
        return True

