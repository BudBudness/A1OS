from api.router import SovereignAPIRouter
from security.core import SovereignSecuritySandbox

sandbox = SovereignSecuritySandbox()

@SovereignAPIRouter.register_route("/security/audit", method="POST")
def security_audit(body):
    if not body or "payload" not in body:
        return 400, {"status": "ERROR", "message": "Missing payload context to verify safety bounds"}
    passed, message = sandbox.audit_string(str(body["payload"]))
    return 200, {"compliant": passed, "assessment": message}
