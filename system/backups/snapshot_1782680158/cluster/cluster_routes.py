from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/cluster/status", method="GET")
def cluster_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "cluster"}
