from modules.intel.intel_worker import IntelWorker
from modules.governance.governance_worker import GovernanceWorker
from modules.ops.ops_worker import OpsWorker

class Orchestrator:
    def __init__(self):
        self.workers = {
            "intel": IntelWorker(),
            "governance": GovernanceWorker(),
            "ops": OpsWorker()
        }

    def get_workers(self):
        return self.workers
