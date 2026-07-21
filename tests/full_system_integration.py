import sys, os
sys.path.append(os.path.expanduser("~/A1OS"))

from modules.finance.accounting import AccountingWorkflow
from modules.research.synthesizer import ResearchSynthesizer
from core.execution.v2.dispatcher.engine import DistributedDispatcher

def test():
    d = DistributedDispatcher()
    d.register("process_data", lambda data: "success")
    
    # 1. Finance Module Integration
    print("--- Testing Finance Module ---")
    fin = AccountingWorkflow()
    # Mocking the interaction: This will hit the gatekeeper
    fin.process_payroll({"task_id": "fin_001", "action": "process_data", "data": {"amount": 100}})

    # 2. Research Module Integration
    print("\n--- Testing Research Module ---")
    res = ResearchSynthesizer()
    res.synthesize("System Hardening", context={"role": "admin"})

if __name__ == "__main__":
    test()
