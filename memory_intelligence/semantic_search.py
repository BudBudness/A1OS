from typing import List, Dict, Optional, Any
from typing import List, Dict, Any
from .models import MemoryItem
from .storage import Storage
from .embeddings import Embeddings
from .vector_store import VectorStore

class SemanticSearch:
    def __init__(self, storage: Storage, embeddings: Embeddings):
        self.storage = storage
        self.embeddings = embeddings
        self.vector_store = VectorStore(storage, embeddings)

    def search(self, query: str, top_k: int = 10, include_types: List[str] = None) -> List[Dict[str, Any]]:
        vector_results = self.vector_store.search(query, top_k)
        results = []
        for item in vector_results:
            if include_types and item.type not in include_types:
                continue
            results.append({
                'id': item.id,
                'content': item.content,
                'type': item.type,
                'timestamp': item.timestamp.isoformat(),
                'metadata': item.metadata,
                'importance': item.importance,
                'score': 0.0  # score from vector search
            })
        return results

    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        # Vector search
        vector_results = self.vector_store.search(query, top_k)
        # Keyword boost
        results = []
        for item in vector_results:
            # Boost if query appears in content
            boost = 0.1 if query.lower() in item.content.lower() else 0.0
            results.append({
                'id': item.id,
                'content': item.content,
                'type': item.type,
                'timestamp': item.timestamp.isoformat(),
                'metadata': item.metadata,
                'importance': item.importance + boost,
                'score': 0.0
            })
        # Sort by boosted importance
        results.sort(key=lambda x: x['importance'], reverse=True)
        return results[:top_k]
