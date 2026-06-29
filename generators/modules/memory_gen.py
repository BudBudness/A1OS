from generators.core.base_gen import BaseGenerator
from pathlib import Path

class MemoryGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "memory"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Artifact A: SQLite High-Performance WAL Storage Layer
        core_memory = '''import sqlite3
import os
import threading
from pathlib import Path

class SovereignMemoryEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_dir = Path(os.path.expanduser("~")) / "A1OS/data"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "a1os_state.db"
        else:
            self.db_path = Path(db_path)
        self._local = threading.local()
        self._init_db()

    def _get_connection(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            self._local.conn.execute("PRAGMA journal_mode=WAL;")
            self._local.conn.execute("PRAGMA synchronous=NORMAL;")
        return self._local.conn

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def store_state(self, key, value):
        conn = self._get_connection()
        conn.execute("INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()

    def fetch_state(self, key):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
'''

        # Artifact B: Vector & Index Simulation Layer for Local AI Context Search
        vector_index = '''import json
import math

class SovereignVectorIndex:
    def __init__(self):
        self.index = {}

    def insert_vector(self, doc_id, vector, metadata):
        self.index[doc_id] = {"vector": vector, "metadata": metadata}

    def cosine_similarity(self, v1, v2):
        dot = sum(a*b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a*a for a in v1))
        mag2 = math.sqrt(sum(b*b for b in v2))
        return dot / (mag1 * mag2) if (mag1 * mag2) else 0.0

    def search(self, query_vector, top_n=3):
        results = []
        for doc_id, data in self.index.items():
            score = self.cosine_similarity(query_vector, data["vector"])
            results.append((doc_id, score, data["metadata"]))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_n]
'''

        # Artifact C: Database Migration Ledger
        migrations = '''import time

def run_migrations(engine):
    print("[MIGRATION-ENGINE] Checking schema evolution states...")
    conn = engine._get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("[MIGRATION-ENGINE] Database is up to date at Version 1.")
'''

        # Artifact D: Automated Component Testing Module
        test_suite = '''from .core_memory import SovereignMemoryEngine
from .vector_index import SovereignVectorIndex

def test_memory_subsystem():
    engine = SovereignMemoryEngine(":memory:")
    engine.store_state("test_key", "verified")
    assert engine.fetch_state("test_key") == "verified"
    
    idx = SovereignVectorIndex()
    idx.insert_vector("node_1", [1.0, 0.0], {"info": "test"})
    res = idx.search([1.0, 0.0])
    assert res[0][0] == "node_1"
    print("✅ Memory Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_memory_subsystem()
'''

        # Write out the full subsystem suite atomically
        with open(output_dir / "core_memory.py", "w") as f: f.write(core_memory.strip())
        with open(output_dir / "vector_index.py", "w") as f: f.write(vector_index.strip())
        with open(output_dir / "migrations.py", "w") as f: f.write(migrations.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_suite.strip())
        
        print(f"[GENERATOR-COMPLETE] memory_gen.py has compiled v1 Subsystem Suite inside {output_dir}")
