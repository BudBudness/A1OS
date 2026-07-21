import asyncio
from company.workers.ops_worker import OpsWorker
from company.workers.procurement_worker import ProcurementWorker
from governance.engine import GovernanceEngine

async def run_optimization():
    ops = OpsWorker()
    proc = ProcurementWorker()
    gov = GovernanceEngine()
    
    report = await ops.execute({})
    if report.get("status") == "action_required":
        action = gov.authorize_optimization(report)
        result = await proc.execute({"action": action})
        print(f"Action: {action} | Result: {result}")
    else:
        print("System optimal")

if __name__ == "__main__":
    asyncio.run(run_optimization())
