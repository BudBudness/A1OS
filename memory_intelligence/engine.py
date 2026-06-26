from typing import List, Dict, Optional, Any
from .storage import Storage
from .embeddings import Embeddings
from .vector_store import VectorStore
from .semantic_search import SemanticSearch
from .episodic import EpisodicMemory
from .working_memory import WorkingMemory
from .long_term import LongTermMemory
from .consolidation import Consolidation
from .retrieval import RetrievalEngine
from .knowledge_graph import KnowledgeGraph
from .models import MemoryItem, MemoryStats

class MemoryEngine:
    def __init__(self, db_path: str = 'data/memory.db'):
        self.storage = Storage(db_path)
        self.embeddings = Embeddings()
        self.vector_store = VectorStore(self.storage, self.embeddings)
        self.semantic_search = SemanticSearch(self.storage, self.embeddings)
        self.episodic = EpisodicMemory(self.storage)
        self.working = WorkingMemory(self.storage)
        self.long_term = LongTermMemory(self.storage)
        self.consolidation = Consolidation(self.storage, self.embeddings)
        self.retrieval = RetrievalEngine(self.storage, self.embeddings)
        self.knowledge_graph = KnowledgeGraph(db_path)

    def add(self, content: str, memory_type: str = 'long_term', metadata: dict = None) -> MemoryItem:
        if memory_type == 'working':
            return self.working.add(content, metadata)
        elif memory_type == 'episodic':
            return self.episodic.add_event(metadata.get('event_type', 'event'), metadata)
        elif memory_type == 'vector':
            return self.vector_store.add(content, metadata)
        else:
            return self.long_term.add(content, metadata)

    def search(self, query: str, top_k: int = 10) -> List[dict]:
        return self.semantic_search.search(query, top_k)

    def retrieve(self, query: str, top_k: int = 20) -> dict:
        return self.retrieval.retrieve(query, top_k)

    def consolidate(self) -> dict:
        return self.consolidation.consolidate_all()

    def get_stats(self) -> MemoryStats:
        return self.storage.get_stats()

    def get_graph(self) -> dict:
        return self.knowledge_graph.get_all_relations()

    def add_relation(self, source: str, target: str, relation: str, metadata: dict = None):
        self.knowledge_graph.add_relation(source, target, relation, metadata)
