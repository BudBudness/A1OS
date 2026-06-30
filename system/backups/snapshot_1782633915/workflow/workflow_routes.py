from api.router import SovereignAPIRouter
from workflow.core import SovereignWorkflowEngine

engine = SovereignWorkflowEngine()

@SovereignAPIRouter.register_route("/workflow/dispatch", method="POST")
def workflow_dispatch(body):
    return 200, {"status": "ACTIVE", "info": engine.dispatch_dag()}
