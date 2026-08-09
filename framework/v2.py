import json
import os
from typing import List, Dict, Any

class ExecutionNode:
    def __init__(self, node_id: str, app_id: str, action: str, context: Dict[str, Any], dependencies: List[str] = None):
        self.node_id = node_id
        self.app_id = app_id
        self.action = action
        self.context = context
        self.dependencies = dependencies or []
        self.status = "PENDING"
        self.result = None

class DAGScheduler:
    def __init__(self, checkpoint_path: str = "deploy/checkpoint.json"):
        self.nodes: Dict[str, ExecutionNode] = {}
        self.checkpoint_path = checkpoint_path

    def add_node(self, node: ExecutionNode):
        self.nodes[node.node_id] = node

    def save_checkpoint(self):
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)
        state = {nid: {"status": n.status, "result": n.result} for nid, n in self.nodes.items()}
        with open(self.checkpoint_path, "w") as f:
            json.dump(state, f)

    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r") as f:
                state = json.load(f)
                for nid, s in state.items():
                    if nid in self.nodes:
                        self.nodes[nid].status = s["status"]
                        self.nodes[nid].result = s["result"]
