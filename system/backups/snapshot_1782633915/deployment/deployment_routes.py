from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/deployment/rollout", method="GET")
def deployment_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "deployment"}
