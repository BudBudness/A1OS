from company.workers.comm_worker import CommWorker
from company.workers.dev_worker import DevWorker
from company.workers.maintenance_worker import MaintenanceWorker
from company.workers.ops_worker import OpsWorker
from company.workers.procurement_worker import ProcurementWorker
from modules.finance.finance_worker import FinanceWorker
from modules.crm.crm_worker import CrmWorker


async def register(runtime):
    workers = {
        "communication": CommWorker(),
        "development": DevWorker(),
        "maintenance": MaintenanceWorker(),
        "operations": OpsWorker(),
        "procurement": ProcurementWorker(),
        "finance": FinanceWorker(),
        "crm": CrmWorker(),
    }

    for name, worker in workers.items():
        await runtime.register_worker(name, worker)
