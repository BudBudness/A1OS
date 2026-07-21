from company.departments.base import Department

class Procurement(Department):
    def __init__(self):
        super().__init__("PROCUREMENT", "CHIEF_OFFICER")
    
    def process_order(self, task):
        # Interface with manufacturers
        print(f"Procuring: {task.payload.get('item')}")
