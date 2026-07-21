from company.workers.comm_worker import CommWorker
from company.workers.dev_worker import DevWorker
from company.workers.maintenance_worker import MaintenanceWorker
from company.workers.ops_worker import OpsWorker
from company.workers.procurement_worker import ProcurementWorker
from modules.trading.trading_worker import TradingWorker
from modules.finance.finance_worker import FinanceWorker
from modules.crm.crm_worker import CRMWorker
import asyncio

def register(runtime):
    workers = {
        "communication": CommWorker(),
        "development": DevWorker(),
        "maintenance": MaintenanceWorker(),
        "operations": OpsWorker(),
        "procurement": ProcurementWorker(),
        "trading": TradingWorker(),
        "finance": FinanceWorker(),
        "crm": CRMWorker()
    }
    
    # Register workers using an event loop to handle the awaitable nature of the registration
    loop = asyncio.get_event_loop()
    for name, worker in workers.items():
        loop.run_until_complete(runtime.register_worker(name, worker))
