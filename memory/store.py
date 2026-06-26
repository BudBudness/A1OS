import hashlib
from datetime import datetime

class MemoryStore:
    def __init__(self):
        self.store = {}

    def add(self, text):
        doc_id = hashlib.md5(text.encode()).hexdigest()
        self.store[doc_id] = {"id": doc_id, "text": text, "created": datetime.now().isoformat()}
        return self.store[doc_id]

    def get_all(self):
        return list(self.store.values())

    def search(self, query):
        q = query.lower()
        return [m for m in self.store.values() if q in m["text"].lower()]