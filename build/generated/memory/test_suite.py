from .core_memory import SovereignMemoryEngine
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