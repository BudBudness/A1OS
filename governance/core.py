from governance.policies.validator import PolicyEngine
from governance.budgets.manager import BudgetManager

class GovernanceCore:
    def __init__(self):
        self.policy = PolicyEngine()
        self.budget = BudgetManager()
    def check_task(self, task):
        return self.policy.validate(task)
