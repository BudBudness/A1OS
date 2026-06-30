from api.router import SovereignAPIRouter
from agent.core import SovereignAgentRuntime

runtime = SovereignAgentRuntime()

@SovereignAPIRouter.register_route("/agent/execute", method="POST")
def agent_execute(body):
    if not body or "role" not in body or "payload" not in body:
        return 400, {"status": "ERROR", "message": "Missing role or payload in instruction context"}
    result = runtime.run_task(body["role"], body["payload"])
    return 200, {"status": "COMPLETED", "execution_frame": result}
