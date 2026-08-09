from typing import Dict, List
import uuid

class ProcurementEngine:
    def __init__(self):
        self.orders: List[Dict] = []
        self.vendors: Dict[str, Dict] = {}
        self.inventory: Dict[str, Dict] = {}
    
    def create_order(self, vendor_id: str, items: List[Dict]) -> str:
        order_id = str(uuid.uuid4())
        self.orders.append({
            "id": order_id,
            "vendor_id": vendor_id,
            "items": items,
            "status": "pending"
        })
        return order_id
    
    def add_vendor(self, name: str, contact: str) -> str:
        vendor_id = str(uuid.uuid4())
        self.vendors[vendor_id] = {
            "id": vendor_id,
            "name": name,
            "contact": contact
        }
        return vendor_id
    
    def update_inventory(self, item_id: str, quantity: int):
        if item_id in self.inventory:
            self.inventory[item_id]["quantity"] += quantity
        else:
            self.inventory[item_id] = {"quantity": quantity}
