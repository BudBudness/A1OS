import json
import math

class SovereignVectorIndex:
    def __init__(self):
        self.index = {}

    def insert_vector(self, doc_id, vector, metadata):
        self.index[doc_id] = {"vector": vector, "metadata": metadata}

    def cosine_similarity(self, v1, v2):
        dot = sum(a*b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a*a for a in v1))
        mag2 = math.sqrt(sum(b*b for b in v2))
        return dot / (mag1 * mag2) if (mag1 * mag2) else 0.0

    def search(self, query_vector, top_n=3):
        results = []
        for doc_id, data in self.index.items():
            score = self.cosine_similarity(query_vector, data["vector"])
            results.append((doc_id, score, data["metadata"]))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_n]