import time

class PeerDiscoveryEngine:
    def __init__(self, topology_manager):
        self.topology = topology_manager
        self.heartbeats = {}

    def receive_heartbeat(self, node_id):
        self.heartbeats[node_id] = time.time()
        # Ensure node is registered in topology upon heartbeat if missing
        if not self.topology.get_node(node_id):
            self.topology.register_node(node_id, "dynamic_peer")

    def prune_dead_nodes(self, max_idle_sec=5.0):
        now = time.time()
        pruned = []
        for node_id, last_seen in list(self.heartbeats.items()):
            if now - last_seen > max_idle_sec:
                self.topology.mark_degraded(node_id)
                pruned.append(node_id)
        return pruned