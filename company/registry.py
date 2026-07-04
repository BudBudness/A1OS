from company.workers.procurement_worker import ProcurementWorker
from company.workers.comm_worker import CommWorker

class AgentRegistry:
    def get_workers(self):
        return {
            "procurement": ProcurementWorker(),
            "comm": CommWorker()
        }
