import sys, os
sys.path.append(os.path.expanduser("~/A1OS"))

from modules.finance.accounting import AccountingWorkflow
from modules.research.synthesizer import ResearchSynthesizer

def test():
    # 1. Finance Module Test
    fin = AccountingWorkflow()
    # Note: Requires registered handler for 'process_data' in workflow engine
    print("Finance module initialized")

    # 2. Research Module Test
    res = ResearchSynthesizer()
    try:
        res.synthesize("AI Architecture", context={"role": "admin"})
        print("Research module synthesized successfully")
    except Exception as e:
        print(f"Research synthesis failed: {e}")

if __name__ == "__main__":
    test()
