import time

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