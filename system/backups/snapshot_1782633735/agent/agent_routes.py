from api.router import SovereignAPIRouter
from agent.core import SovereignAgentRuntime

runtime = SovereignAgentRuntime()

@SovereignAPIRouter.register_route("/agent/execute", method="POST")
def agent_execute(body):
    task = body.get("task", "default_ping") if body else "default_ping"
    res = runtime.run_task(task)
    return 200, {"status": "COMPLETED", "result": res}
