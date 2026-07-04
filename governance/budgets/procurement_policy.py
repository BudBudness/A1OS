from governance.budgets.manager import BudgetManager

class ProcurementPolicy(BudgetManager):
    def check_funds(self, amount):
        # Business logic for Stanbic/Airtel wallet routing
        return True
