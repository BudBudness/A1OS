import app

REQUIRED = {
    "/",
    "/v1/health",
    "/v1/ready",
    "/v1/readiness",
    "/v1/auth/login",
    "/v1/auth/me",
    "/v1/organizations",
    "/v1/users",
    "/v1/roles",
    "/v1/parties",
    "/v1/products",
    "/v1/accounts",
    "/v1/ledger",
    "/v1/ledger/balances",
    "/v1/inventory/items",
    "/v1/notifications",
    "/v1/audit",
}

def test_a1os_api_surface_is_intact():
    routes = {
        route.path
        for route in app.app.routes
        if getattr(route, "path", None)
    }
    assert REQUIRED <= routes
    assert not any(r.lower().startswith("/api/") and "status" in r.lower() for r in routes)
    assert not any("/professional-" in r.lower() for r in routes)
