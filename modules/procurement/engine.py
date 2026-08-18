from typing import Dict, List
import uuid

class ProcurementEngine:
    async def execute(self, action, **kwargs):
        method = getattr(self, action, None)

        if method is None or not callable(method):
            raise RuntimeError(
                f"Procurement engine has no compatible action: {action}"
            )

        data = kwargs.pop("data", {})
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise TypeError("Procurement execution data must be a dictionary")

        arguments = {
            key: value
            for key, value in kwargs.items()
            if key not in {"target", "action", "role"}
        }
        arguments.update(data)

        result = method(**arguments)
        if hasattr(result, "__await__"):
            return await result
        return result


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
