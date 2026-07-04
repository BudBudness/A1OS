from modules.procurement.procurement import Procurement
import json
import os

class ProcurementWorker:
    def __init__(self):
        self.engine = Procurement()
        self.state_path = 'data/procurement/state.json'

    def process_task(self, item, quantity):
        result = self.engine.execute('BUY', item, quantity)
        if "Success" in result:
            self._update_state(item, quantity)
        return result

    def _update_state(self, item, quantity):
        data = {"item": item, "quantity": quantity, "status": "processed"}
        with open(self.state_path, 'w') as f:
            json.dump(data, f, indent=4)
