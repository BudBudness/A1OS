from typing import List, Dict, Optional, Any
from typing import List, Dict, Any, Optional
from .models import MemoryItem
from .storage import Storage
from .embeddings import Embeddings
import hashlib
from datetime import datetime

class VectorStore:
    def __init__(self, storage: Storage, embeddings: Embeddings):
        self.storage = storage
        self.embeddings = embeddings
        self._cache = {}

    def add(self, content: str, metadata: dict = None) -> MemoryItem:
        item_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()
        embedding = self.embeddings.encode(content)
        item = MemoryItem(
            id=item_id,
            content=content,
            type='vector',
            metadata=metadata or {},
            embedding=embedding
        )
        self.storage.save(item)
        self._cache[item_id] = embedding
        return item

    def search(self, query: str, top_k: int = 10) -> List[MemoryItem]:
        query_vec = self.embeddings.encode(query)
        items = self.storage.get_all('vector')
        results = []
        for item in items:
            emb = self._cache.get(item.id) or self.embeddings.encode(item.content)
            self._cache[item.id] = emb
            score = self.embeddings.similarity(query_vec, emb)
            results.append((item, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in results[:top_k]]

    def get_by_id(self, item_id: str) -> Optional[MemoryItem]:
        return self.storage.get(item_id)

    def delete(self, item_id: str):
        self.storage.delete(item_id)
        self._cache.pop(item_id, None)
