from modules.intel.intel_worker import IntelWorker
from modules.governance.governance_worker import GovernanceWorker
from modules.ops.ops_worker import OpsWorker
from modules.crm.crm_worker import CRMWorker
from modules.analytics.analytics_worker import AnalyticsWorker

class Orchestrator:
    def __init__(self):
        self.workers = {
            "intel": IntelWorker(),
            "governance": GovernanceWorker(),
            "ops": OpsWorker(),
            "crm": CRMWorker(),
            "analytics": AnalyticsWorker()
        }

    def get_workers(self):
        return self.workers
