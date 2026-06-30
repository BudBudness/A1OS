from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/tests/run", method="GET")
def tests_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "tests"}
