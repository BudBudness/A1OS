from typing import Dict, Any, Optional
import time

class MemoryEngine:
    def __init__(self):
        self.short_term: Dict[str, Any] = {}
        self.long_term: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any, memory_type: str = "short"):
        if memory_type == "short":
            self.short_term[key] = {"value": value, "timestamp": time.time()}
        else:
            self.long_term[key] = {"value": value, "timestamp": time.time()}
    
    def recall(self, key: str, context: Optional[Dict] = None) -> Optional[Any]:
        if key in self.short_term:
            return self.short_term[key]["value"]
        return self.long_term.get(key, {}).get("value")
    
    def update_context(self, key: str, value: Any):
        self.context[key] = value
