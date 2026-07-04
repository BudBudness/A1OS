from typing import List, Dict, Any
from framework.v2 import DAGScheduler, ExecutionNode

class AICompanyOrchestrator:
    def __init__(self, runtime):
        self.runtime = runtime
        self.scheduler = DAGScheduler()

    def orchestrate_objective(self, objective: str, steps: List[Dict[str, Any]]):
        self.runtime.logger.log("INFO", f"Orchestrating objective: {objective}")
        for i, step in enumerate(steps):
            node = ExecutionNode(
                node_id=f"step_{i}",
                app_id=step["app_id"],
                action=step["action"],
                context=step.get("context", {}),
                dependencies=[f"step_{i-1}"] if i > 0 else []
            )
            self.scheduler.add_node(node)
        
        for nid, node in self.scheduler.nodes.items():
            for dep in node.dependencies:
                if self.scheduler.nodes[dep].status != "COMPLETED":
                    self.runtime.logger.log("WARN", f"Dependency {dep} missing for {nid}")
            
            if node.status != "COMPLETED":
                self.runtime.execute_app(node.app_id, node.action, node.context)
                node.status = "COMPLETED"
        self.scheduler.save_checkpoint()
