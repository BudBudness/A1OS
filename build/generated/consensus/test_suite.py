from .engine import DistributedConsensusEngine
from .validator import StateChangeValidator
from .ledger import AppendOnlyStateLedger

def test_consensus_subsystem():
    # 1. Node election and term increment validation
    engine = DistributedConsensusEngine("node_1")
    engine.start_election()
    assert engine.state == "candidate"
    assert engine.current_term == 1
    
    # 2. Remote vote acceptance checks
    assert engine.cast_vote("node_2", 2) is True
    assert engine.current_term == 2
    
    # 3. Ledger append and state change validation
    ledger = AppendOnlyStateLedger()
    validator = StateChangeValidator(ledger)
    
    entry = ledger.append_state("abc123hash", {"action": "SYSTEM_BOOT"})
    assert ledger.get_last_entry()["index"] == 0
    
    is_valid, reason = validator.validate_proposal({
        "prev_hash": "abc123hash",
        "hash": "xyz789hash",
        "payload": {"action": "STATE_UPDATE"}
    })
    assert is_valid is True
    
    print("✅ Distributed Consensus Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_consensus_subsystem()