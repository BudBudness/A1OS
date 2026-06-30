from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/backup/trigger", method="GET")
def backup_endpoint_handler(body):
    return 200, {"status": "ONLINE", "subsystem": "backup"}
