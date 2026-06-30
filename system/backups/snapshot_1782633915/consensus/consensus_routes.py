from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/consensus/state", method="GET")
def consensus_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "consensus"}
