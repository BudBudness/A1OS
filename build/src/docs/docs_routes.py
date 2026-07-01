from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/docs/render", method="GET")
def docs_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "docs"}
