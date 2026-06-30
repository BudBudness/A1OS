from api.router import SovereignAPIRouter
from memory.core import SovereignMemoryEngine

engine = SovereignMemoryEngine()

@SovereignAPIRouter.register_route("/memory/store", method="POST")
def store_data(body):
    if not body or "key" not in body or "value" not in body:
        return 400, {"status": "ERROR", "message": "Missing key or value"}
    engine.set(body["key"], body["value"])
    return 200, {"status": "SUCCESS", "stored": body["key"]}

@SovereignAPIRouter.register_route("/memory/retrieve", method="POST")
def retrieve_data(body):
    if not body or "key" not in body:
        return 400, {"status": "ERROR", "message": "Missing key"}
    val = engine.get(body["key"])
    return 200, {"status": "SUCCESS", "key": body["key"], "value": val}
