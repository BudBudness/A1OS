import threading
from organization.departments.base_department import BaseDepartment

class FinanceDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("Finance", "CFO_Bot")
        self.kpis = {"budget": 1000000, "spent": 0}
        self.lock = threading.Lock()

    def can_afford(self, amount):
        with self.lock:
            return (self.kpis["budget"] - self.kpis["spent"]) >= amount

    def record_spend(self, amount):
        with self.lock:
            self.kpis["spent"] += amount
