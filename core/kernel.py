from company.orchestrator import Orchestrator
from company.workers.procurement_worker import ProcurementWorker
import json
import os

class Kernel:
    def __init__(self):
        self.orch = Orchestrator()
        self.worker = ProcurementWorker()
        self.task_dir = 'data/tasks/pending'

    def run_full_cycle(self):
        for task_file in os.listdir(self.task_dir):
            path = os.path.join(self.task_dir, task_file)
            with open(path, 'r') as f:
                task = json.load(f)
                result = self.worker.process_task(task['item'], task['quantity'])
                os.remove(path)
                return result
