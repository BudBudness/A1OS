from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/domainpack/view", method="GET")
def domainpack_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "domainpack"}
