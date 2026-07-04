import json

class IntentParser:
    def parse(self, text):
        # Basic logic: maps keywords to task types
        if "order" in text.lower():
            # Example: "Order 100 Artificial Grass"
            parts = text.split()
            return {
                "action": "order_supplies",
                "item": " ".join(parts[2:]),
                "quantity": int(parts[1])
            }
        return None
