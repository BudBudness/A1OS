from typing import Dict, List, Any
import uuid

class DistributedEngine:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}
        self.results: Dict[str, Any] = {}
    
    def register_node(self, node_id: str, capabilities: List[str]):
        self.nodes[node_id] = {
            "id": node_id,
            "capabilities": capabilities,
            "status": "online"
        }
    
    async def submit_task(self, task_type: str, payload: Dict) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "payload": payload,
            "status": "pending"
        }
        return task_id
    
    async def get_result(self, task_id: str) -> Any:
        return self.results.get(task_id)
    
    def _assign_node(self, task_type: str) -> str:
        for node_id, node in self.nodes.items():
            if task_type in node["capabilities"]:
                return node_id
        return None
