class TopologyStateReplicator:
    def __init__(self):
        self.replicated_state = {}

    def push_delta(self, delta_id, state_payload):
        self.replicated_state[delta_id] = state_payload
        print(f"[TOPOLOGY-SYNC] State replicated delta #{delta_id}")

    def pull_delta(self, delta_id):
        return self.replicated_state.get(delta_id)