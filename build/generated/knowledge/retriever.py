class KnowledgeRetriever:
    def __init__(self, store_instance):
        self.store = store_instance

    def query_by_category(self, category_filter):
        cursor = self.store._conn.cursor()
        cursor.execute("SELECT entity_id, content FROM long_term_knowledge WHERE category = ?", (category_filter,))
        return [{"entity_id": row[0], "content": row[1]} for row in cursor.fetchall()]