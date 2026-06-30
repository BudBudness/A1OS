from api.router import SovereignAPIRouter
from knowledge.core import SovereignKnowledgeGraph

graph = SovereignKnowledgeGraph()

@SovereignAPIRouter.register_route("/knowledge/link", method="POST")
def link_knowledge(body):
    if not body or not all(k in body for k in ["source", "relation", "target"]):
        return 400, {"status": "ERROR", "message": "Missing source, relation, or target semantic elements"}
    graph.link_entities(body["source"], body["relation"], body["target"])
    return 200, {"status": "LINKED", "edges_count": len(graph.edges)}

@SovereignAPIRouter.register_route("/knowledge/query", method="GET")
def query_knowledge(body):
    return 200, {
        "graph_status": "ONLINE",
        "distinct_nodes": list(graph.nodes.keys()),
        "semantic_edges": graph.edges
    }
