from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/monitoring/metrics", method="GET")
def monitoring_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "monitoring"}
