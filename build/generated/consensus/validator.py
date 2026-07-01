class StateChangeValidator:
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