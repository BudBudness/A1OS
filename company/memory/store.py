from typing import Dict, Any

class MemoryLayer:
    def __init__(self):
        self.store: Dict[str, Any] = {}
        
    def save(self, key: str, value: Any):
        self.store[key] = value
        
    def retrieve(self, key: str) -> Any:
        return self.store.get(key)

