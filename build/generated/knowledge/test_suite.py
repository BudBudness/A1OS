import time
from .store import LongTermMemoryStore
from .retriever import KnowledgeRetriever
from .mapper import KnowledgeRelationshipMapper

def test_knowledge_subsystem():
    store = LongTermMemoryStore(":memory:")
    retriever = KnowledgeRetriever(store)
    mapper = KnowledgeRelationshipMapper()
    
    # 1. Store and fetch long-term records
    now = time.time()
    store.insert_knowledge("entity_001", "Sovereign OS Kernel Blueprint", "core_concept", now)
    record = store.fetch_knowledge("entity_001")
    assert record is not None
    assert record["category"] == "core_concept"
    
    # 2. Query retrieval validation
    results = retriever.query_by_category("core_concept")
    assert len(results) == 1
    assert results[0]["entity_id"] == "entity_001"
    
    # 3. Relationship dependency mapping validation
    mapper.map_relation("entity_001", "entity_002", "DEPENDS_ON")
    relations = mapper.get_relations("entity_001")
    assert len(relations) == 1
    assert relations[0]["target"] == "entity_002"
    
    print("✅ Long-term Knowledge Storage Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_knowledge_subsystem()