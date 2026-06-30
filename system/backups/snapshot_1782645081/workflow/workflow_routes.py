from api.router import SovereignAPIRouter
from workflow.core import SovereignWorkflowEngine

engine = SovereignWorkflowEngine()

@SovereignAPIRouter.register_route("/workflow/dispatch", method="POST")
def workflow_dispatch(body):
    if not body or "steps" not in body or not isinstance(body["steps"], list):
        return 400, {"status": "ERROR", "message": "Expected a list of topological workflow 'steps'"}
    trace = engine.execute_dag(body["steps"])
    return 200, {
        "status": "DAG_FLUSHED",
        "total_nodes_executed": len(trace),
        "trace": trace
    }
