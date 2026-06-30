from api.router import SovereignAPIRouter
@SovereignAPIRouter.register_route("/knowledge/query", method="GET")
def query_knowledge(body):
    return 200, {"graph_status": "ONLINE", "nodes_count": 0}
