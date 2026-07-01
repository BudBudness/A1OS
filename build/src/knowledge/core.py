class SovereignKnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
    def link_entities(self, source, relation, target):
        self.nodes[source] = True
        self.nodes[target] = True
        self.edges.append({"source": source, "relation": relation, "target": target})
        return True
