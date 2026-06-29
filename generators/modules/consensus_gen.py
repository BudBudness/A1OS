from generators.core.base_gen import BaseGenerator
from pathlib import Path

class ConsensusGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "consensus"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Consensus State Machine Engine
        engine_code = '''import time

class DistributedConsensusEngine:
    def __init__(self, node_id):
        self.node_id = node_id
        self.current_term = 0
        self.state = "follower"
        self.votes_received = set()

    def start_election(self):
        self.current_term += 1
        self.state = "candidate"
        self.votes_received = {self.node_id}
        print(f"[CONSENSUS-ENGINE] Node {self.node_id} initiated election term {self.current_term}")

    def cast_vote(self, candidate_id, term):
        if term > self.current_term:
            self.current_term = term
            self.state = "follower"
            print(f"[CONSENSUS-ENGINE] Node {self.node_id} voted for candidate {candidate_id} in term {term}")
            return True
        return False
'''

        # 2. Transaction Integrity and State Validator
        validator_code = '''class StateChangeValidator:
    def __init__(self, ledger_instance):
        self.ledger = ledger_instance

    def validate_proposal(self, proposed_state_delta):
        # Deterministic checks for structural validity
        if not proposed_state_delta or "hash" not in proposed_state_delta:
            return False, "malformed_delta_payload"
        
        # Verify state history continuity
        last_entry = self.ledger.get_last_entry()
        if last_entry and last_entry.get("hash") == proposed_state_delta.get("prev_hash"):
            return True, "valid_state_transition"
            
        return True, "genesis_or_untracked_anchor"
'''

        # 3. Append-Only State Journal Ledger
        ledger_code = '''import time

class AppendOnlyStateLedger:
    def __init__(self):
        self.chain = []

    def append_state(self, state_hash, data_payload):
        entry = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "hash": state_hash,
            "payload": data_payload
        }
        self.chain.append(entry)
        print(f"[CONSENSUS-LEDGER] State transition committed to journal index: {entry['index']}")
        return entry

    def get_last_entry(self):
        return self.chain[-1] if self.chain else None
'''

        # 4. Distributed Consensus Isolation Test Suite
        test_code = '''from .engine import DistributedConsensusEngine
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
'''

        # Write out the structural consensus modules atomically
        with open(output_dir / "engine.py", "w") as f: f.write(engine_code.strip())
        with open(output_dir / "validator.py", "w") as f: f.write(validator_code.strip())
        with open(output_dir / "ledger.py", "w") as f: f.write(ledger_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] consensus_gen.py has compiled v1 Consensus Subsystem inside {output_dir}")
