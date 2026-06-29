from generators.core.base_gen import BaseGenerator
from pathlib import Path

class ClusterGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "cluster"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Cluster Indexing and Node State Mapping Engine
        topology_code = '''import time

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
'''

        # 2. Peer Registration and Heartbeat Tracking Mechanism
        discovery_code = '''import time

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
'''

        # 3. State Replication Utility
        sync_code = '''class TopologyStateReplicator:
    def __init__(self):
        self.replicated_state = {}

    def push_delta(self, delta_id, state_payload):
        self.replicated_state[delta_id] = state_payload
        print(f"[TOPOLOGY-SYNC] State replicated delta #{delta_id}")

    def pull_delta(self, delta_id):
        return self.replicated_state.get(delta_id)
'''

        # 4. Multi-node Discovery Component Verification Suite
        test_code = '''import time
from .topology import ClusterTopologyManager
from .discovery import PeerDiscoveryEngine
from .sync import TopologyStateReplicator

def test_cluster_subsystem():
    topology = ClusterTopologyManager()
    discovery = PeerDiscoveryEngine(topology)
    replicator = TopologyStateReplicator()
    
    # 1. Register operational nodes
    topology.register_node("node_alpha", "10.0.0.5", "controller")
    assert topology.get_node("node_alpha")["role"] == "controller"
    
    # 2. Peer heartbeat verification
    discovery.receive_heartbeat("node_beta")
    assert topology.get_node("node_beta") is not None
    
    # 3. Node pruning evaluation
    discovery.receive_heartbeat("node_gamma")
    time.sleep(0.2)
    pruned = discovery.prune_dead_nodes(max_idle_sec=0.1)
    assert "node_gamma" in pruned
    
    # 4. State replication assertion
    replicator.push_delta(101, {"topology_hash": "abc123xyz"})
    assert replicator.pull_delta(101)["topology_hash"] == "abc123xyz"
    
    print("✅ Cluster Topology Discovery Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_cluster_subsystem()
'''

        # Write out the full structural cluster module files atomically
        with open(output_dir / "topology.py", "w") as f: f.write(topology_code.strip())
        with open(output_dir / "discovery.py", "w") as f: f.write(discovery_code.strip())
        with open(output_dir / "sync.py", "w") as f: f.write(sync_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] cluster_gen.py has compiled v1 Cluster Subsystem inside {output_dir}")
