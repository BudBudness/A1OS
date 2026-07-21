from orchestration.workflow.engine import WorkflowEngine

class AccountingWorkflow:
    def __init__(self):
        self.engine = WorkflowEngine()

    def process_payroll(self, payroll_data):
        self.engine.add_step("pay_001", "process_data", payroll_data)
        return self.engine.run_dag()
