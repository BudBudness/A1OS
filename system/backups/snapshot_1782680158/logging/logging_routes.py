from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/logging/flush", method="GET")
def logging_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "logging"}
