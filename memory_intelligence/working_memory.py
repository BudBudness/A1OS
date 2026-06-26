from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib
from .models import MemoryItem
from .storage import Storage

class WorkingMemory:
    def __init__(self, storage: Storage, ttl_seconds: int = 300):
        self.storage = storage
        self.ttl = ttl_seconds

    def add(self, content: str, metadata: dict = None) -> MemoryItem:
        item_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()
        item = MemoryItem(
            id=item_id,
            content=content,
            type='working',
            metadata=metadata or {},
            expires_at=datetime.now() + timedelta(seconds=self.ttl)
        )
        self.storage.save(item)
        return item

    def get_active(self) -> List[MemoryItem]:
        now = datetime.now()
        items = self.storage.get_all('working')
        active = [i for i in items if not i.expires_at or i.expires_at > now]
        return active

    def expire_old(self):
        now = datetime.now()
        items = self.storage.get_all('working')
        expired = [i.id for i in items if i.expires_at and i.expires_at <= now]
        for item_id in expired:
            self.storage.delete(item_id)
        return len(expired)

    def promote_to_long_term(self, item_id: str) -> Optional[MemoryItem]:
        item = self.storage.get(item_id)
        if not item or item.type != 'working':
            return None
        item.type = 'long_term'
        item.expires_at = None
        self.storage.save(item)
        return item
