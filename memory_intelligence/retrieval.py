from typing import List, Dict, Optional, Any
from typing import List, Dict, Any, Optional
from .storage import Storage
from .embeddings import Embeddings
from .semantic_search import SemanticSearch
from .episodic import EpisodicMemory
from .working_memory import WorkingMemory
from .long_term import LongTermMemory
from .knowledge_graph import KnowledgeGraph

class RetrievalEngine:
    def __init__(self, storage: Storage, embeddings: Embeddings):
        self.storage = storage
        self.embeddings = embeddings
        self.semantic = SemanticSearch(storage, embeddings)
        self.episodic = EpisodicMemory(storage)
        self.working = WorkingMemory(storage)
        self.long_term = LongTermMemory(storage)
        self.graph = KnowledgeGraph()

    def retrieve(self, query: str, top_k: int = 20) -> Dict[str, Any]:
        results = {
            'query': query,
            'working_memory': [],
            'episodic': [],
            'long_term': [],
            'vector': [],
            'graph': [],
            'merged': []
        }

        # Search each memory type
        vector_results = self.semantic.search(query, top_k=5)
        results['vector'] = vector_results

        working_items = self.working.get_active()
        for item in working_items:
            if query.lower() in item.content.lower():
                results['working_memory'].append(item.to_dict())

        episodic_items = self.episodic.get_recent(10)
        for item in episodic_items:
            if query.lower() in item.content.lower():
                results['episodic'].append(item.to_dict())

        long_term_items = self.long_term.search(query)
        results['long_term'] = [item.to_dict() for item in long_term_items[:5]]

        # Graph results
        graph_relations = self.graph.get_all_relations()
        for rel in graph_relations:
            if query.lower() in rel['source'].lower() or query.lower() in rel['target'].lower():
                results['graph'].append(rel)

        # Merge all results
        merged = []
        all_items = results['working_memory'] + results['episodic'] + results['long_term'] + results['vector']
        seen_ids = set()
        for item in all_items:
            if isinstance(item, dict) and item.get('id') not in seen_ids:
                seen_ids.add(item.get('id'))
                merged.append(item)
        results['merged'] = merged[:top_k]

        return results
