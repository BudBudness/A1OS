from typing import List, Dict, Optional, Any
from datetime import datetime
from typing import List, Optional
import hashlib
from .models import MemoryItem
from .storage import Storage

class LongTermMemory:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add(self, content: str, metadata: dict = None, importance: float = 0.0) -> MemoryItem:
        item_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()
        item = MemoryItem(
            id=item_id,
            content=content,
            type='long_term',
            metadata=metadata or {},
            importance=importance
        )
        self.storage.save(item)
        return item

    def get_all(self) -> List[MemoryItem]:
        return self.storage.get_all('long_term')

    def get_by_importance(self, min_importance: float = 0.5) -> List[MemoryItem]:
        items = self.storage.get_all('long_term')
        return [i for i in items if i.importance >= min_importance]

    def update_importance(self, item_id: str, importance: float):
        item = self.storage.get(item_id)
        if item:
            item.importance = importance
            self.storage.save(item)

    def search(self, query: str) -> List[MemoryItem]:
        items = self.storage.get_all('long_term')
        query_lower = query.lower()
        return [i for i in items if query_lower in i.content.lower()]
