import time

class ClusterTopologyManager:
    def __init__(self):
        self.nodes = {}

    def register_node(self, node_id, address, role="worker"):
        self.nodes[node_id] = {
            "address": address,
            "role": role,
            "registered_at": time.time(),
            "status": "active"
        }
        print(f"[TOPOLOGY-MGR] Mapped operational state for cluster node: {node_id} at {address}")

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def mark_degraded(self, node_id):
        if node_id in self.nodes:
            self.nodes[node_id]["status"] = "degraded"
            print(f"[TOPOLOGY-MGR] Node state marked degraded: {node_id}")