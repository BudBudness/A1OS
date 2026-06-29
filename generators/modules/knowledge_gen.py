from generators.core.base_gen import BaseGenerator
from pathlib import Path

class KnowledgeGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "knowledge"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Long-term Data Memory Entity Storage Engine
        store_code = '''import sqlite3
from pathlib import Path

class LongTermMemoryStore:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_table()

    def _init_table(self):
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_knowledge (
                    entity_id TEXT PRIMARY KEY,
                    content TEXT,
                    category TEXT,
                    created_at REAL
                )
            """)

    def insert_knowledge(self, entity_id, content, category, timestamp):
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO long_term_knowledge VALUES (?, ?, ?, ?)",
                (entity_id, content, category, timestamp)
            )
        print(f"[KNOWLEDGE-STORE] Stored long-term entity record: {entity_id}")

    def fetch_knowledge(self, entity_id):
        cursor = self._conn.cursor()
        cursor.execute("SELECT content, category FROM long_term_knowledge WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        return {"content": row[0], "category": row[1]} if row else None
'''

        # 2. Contextual Query Retrieval Parser
        retriever_code = '''class KnowledgeRetriever:
    def __init__(self, store_instance):
        self.store = store_instance

    def query_by_category(self, category_filter):
        cursor = self.store._conn.cursor()
        cursor.execute("SELECT entity_id, content FROM long_term_knowledge WHERE category = ?", (category_filter,))
        return [{"entity_id": row[0], "content": row[1]} for row in cursor.fetchall()]
'''

        # 3. Structural Metadata Relationship Mapper
        mapper_code = '''class KnowledgeRelationshipMapper:
    def __init__(self):
        self._graph = {}

    def map_relation(self, source_id, target_id, relation_type):
        if source_id not in self._graph:
            self._graph[source_id] = []
        self._graph[source_id].append({"target": target_id, "type": relation_type})
        print(f"[KNOWLEDGE-MAPPER] Mapped dependency trace: {source_id} --({relation_type})--> {target_id}")

    def get_relations(self, entity_id):
        return self._graph.get(entity_id, [])
'''

        # 4. Long-Term Memory Integration Component Verification Suite
        test_code = '''import time
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
'''

        # Write out the full structural knowledge module files atomically
        with open(output_dir / "store.py", "w") as f: f.write(store_code.strip())
        with open(output_dir / "retriever.py", "w") as f: f.write(retriever_code.strip())
        with open(output_dir / "mapper.py", "w") as f: f.write(mapper_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] knowledge_gen.py has compiled v1 Knowledge Subsystem inside {output_dir}")
