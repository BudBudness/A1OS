from typing import List, Dict, Optional, Any
from datetime import datetime
from typing import List, Optional
import hashlib
from .models import MemoryItem
from .storage import Storage

class EpisodicMemory:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_event(self, event_type: str, data: dict) -> MemoryItem:
        content = f"{event_type}: {data}"
        item_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()
        item = MemoryItem(
            id=item_id,
            content=content,
            type='episodic',
            metadata={'event_type': event_type, 'data': data}
        )
        self.storage.save(item)
        return item

    def get_by_time_range(self, start: datetime, end: datetime) -> List[MemoryItem]:
        items = self.storage.get_all('episodic')
        return [i for i in items if start <= i.timestamp <= end]

    def get_by_event_type(self, event_type: str) -> List[MemoryItem]:
        items = self.storage.get_all('episodic')
        return [i for i in items if i.metadata.get('event_type') == event_type]

    def get_recent(self, limit: int = 20) -> List[MemoryItem]:
        items = self.storage.get_all('episodic')
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[:limit]
