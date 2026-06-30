from api.router import SovereignAPIRouter

@SovereignAPIRouter.register_route("/health", method="GET")
def health_endpoint(body):
    return 200, {"status": "HEALTHY", "gateway": "ALIVE"}

@SovereignAPIRouter.register_route("/routes", method="GET")
def routes_endpoint(body):
    # Enumerate nested dictionary route maps dynamically
    active_paths = sorted(list(SovereignAPIRouter.routes.keys()))
    return 200, {"routes": active_paths}

@SovereignAPIRouter.register_route("/system/status", method="GET")
def status_endpoint(body):
    return 200, {
        "status": "OPERATIONAL",
        "matrix_mode": "SINGLE_PROCESS_MICROKERNEL",
        "subsystems_loaded": len(SovereignAPIRouter.routes)
    }

@SovereignAPIRouter.register_route("/openapi", method="GET")
def openapi_endpoint(body):
    schema = {"openapi": "3.0.0", "info": {"title": "A1OS Sovereign API", "version": "1.0.0"}, "paths": {}}
    for path, methods in SovereignAPIRouter.routes.items():
        schema["paths"][path] = {m.lower(): {"responses": {"200": {"description": "Success"}}} for m in methods}
    return 200, schema
