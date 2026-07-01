class KnowledgeRelationshipMapper:
    def __init__(self):
        self._graph = {}

    def map_relation(self, source_id, target_id, relation_type):
        if source_id not in self._graph:
            self._graph[source_id] = []
        self._graph[source_id].append({"target": target_id, "type": relation_type})
        print(f"[KNOWLEDGE-MAPPER] Mapped dependency trace: {source_id} --({relation_type})--> {target_id}")

    def get_relations(self, entity_id):
        return self._graph.get(entity_id, [])