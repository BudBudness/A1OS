from company.workers.comm_worker import CommWorker
from company.workers.dev_worker import DevWorker
from company.workers.maintenance_worker import MaintenanceWorker
from company.workers.ops_worker import OpsWorker
from company.workers.procurement_worker import ProcurementWorker
from modules.finance.finance_worker import FinanceWorker
from modules.crm.crm_worker import CrmWorker
import asyncio

def register(runtime):
    workers = {
        "communication": CommWorker(),
        "development": DevWorker(),
        "maintenance": MaintenanceWorker(),
        "operations": OpsWorker(),
        "procurement": ProcurementWorker(),
        "finance": FinanceWorker(),
        "crm": CrmWorker()
    }
    
    # Register workers using an event loop to handle the awaitable nature of the registration
    async def _register_all():
        for name, worker in workers.items():
            await runtime.register_worker(name, worker)

    asyncio.run(_register_all())
