from typing import List, Dict, Optional, Any
from typing import List, Optional, Dict
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional
from .models import MemoryItem
from .storage import Storage
from .embeddings import Embeddings

class Consolidation:
    def __init__(self, storage: Storage, embeddings: Embeddings, similarity_threshold: float = 0.85):
        self.storage = storage
        self.embeddings = embeddings
        self.threshold = similarity_threshold

    def consolidate(self, memory_type: Optional[str] = None) -> Dict:
        items = self.storage.get_all(memory_type)
        removed = 0
        promoted = 0

        # Remove duplicates based on content similarity
        seen = {}
        for item in items:
            emb = self.embeddings.encode(item.content)
            is_duplicate = False
            for existing_id, existing_emb in seen.items():
                if self.embeddings.similarity(emb, existing_emb) > self.threshold:
                    is_duplicate = True
                    break
            if is_duplicate:
                self.storage.delete(item.id)
                removed += 1
            else:
                seen[item.id] = emb

        # Promote important working memory to long-term
        working_items = self.storage.get_all('working')
        for item in working_items:
            if item.importance > 0.5 and item.expires_at:
                item.type = 'long_term'
                item.expires_at = None
                self.storage.save(item)
                promoted += 1

        return {
            'removed_duplicates': removed,
            'promoted_to_long_term': promoted,
            'timestamp': datetime.now().isoformat()
        }

    def consolidate_all(self) -> Dict:
        return self.consolidate()
