from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/scheduler/jobs", method="GET")
def scheduler_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "scheduler"}
