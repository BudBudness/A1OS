from modules.base import BaseModule

class Procurement(BaseModule):
    def execute(self, action, **kwargs):
        if action == "order_supplies":
            return self._order_supplies(kwargs)
        return "Unknown action."

    def _order_supplies(self, params):
        item = params.get('item')
        qty = params.get('quantity')
        self.save_state({"last_order": item, "qty": qty})
        return f"Procurement order placed for {qty} units of {item}."
