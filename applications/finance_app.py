from applications.base_app import BaseApplication
from sdk.worker_sdk import WorkerSDK
from core.registry import SystemRegistry

class FinanceApp(BaseApplication):
    def __init__(self):
        super().__init__(
            name="Finance Treasury Manager",
            description="Governs company capital.",
            required_plugins=["accounting"]
        )
        self.worker = WorkerSDK("CFO_Bot", "Chief Financial Officer", "Finance")

    def run(self, amount, recipient, reason):
        finance_dept = SystemRegistry.get_department("Finance")
        
        # Governance Gate
        if not finance_dept or not finance_dept.can_afford(amount):
            # LOG THE FAILURE
            self.worker.logger.log("CFO_Bot", "Execute Payment", f"Denied: Insufficient Funds for {amount}", "failed")
            return "Transaction Denied: Insufficient Funds"

        finance_dept.record_spend(amount)
        return self.worker.perform_task("Execute Payment", lambda: f"Transferred {amount} to {recipient}")
