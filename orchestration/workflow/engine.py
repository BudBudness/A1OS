from typing import Dict, List, Any
import uuid

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Dict] = {}
        self.running_instances: Dict[str, Dict] = {}
    
    def register(self, workflow_id: str, steps: List[Dict]):
        self.workflows[workflow_id] = {"steps": steps, "id": workflow_id}
    
    async def execute(self, workflow_id: str, context: Dict) -> Dict:
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        instance_id = str(uuid.uuid4())
        workflow = self.workflows[workflow_id]
        results = []
        for step in workflow["steps"]:
            if "action" in step:
                result = await self._execute_action(step["action"], context)
                results.append(result)
                context.update(result)
        return {"instance_id": instance_id, "results": results}
    
    async def _execute_action(self, action: str, context: Dict) -> Dict:
        return {"status": "completed", "action": action}
