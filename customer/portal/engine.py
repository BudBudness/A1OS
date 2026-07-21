from typing import Dict, List
import uuid

class CustomerPortal:
    def __init__(self):
        self.tickets: List[Dict] = []
        self.knowledge_base: List[Dict] = []
    
    def create_ticket(self, customer_id: str, subject: str, message: str) -> str:
        ticket_id = str(uuid.uuid4())
        self.tickets.append({
            "id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "message": message,
            "status": "open"
        })
        return ticket_id
    
    def add_article(self, title: str, content: str, category: str) -> str:
        article_id = str(uuid.uuid4())
        self.knowledge_base.append({
            "id": article_id,
            "title": title,
            "content": content,
            "category": category
        })
        return article_id
    
    def search_articles(self, query: str) -> List[Dict]:
        results = []
        for article in self.knowledge_base:
            if query.lower() in article["title"].lower() or query.lower() in article["content"].lower():
                results.append(article)
        return results
