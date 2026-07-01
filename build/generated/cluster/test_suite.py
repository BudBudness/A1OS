import time
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