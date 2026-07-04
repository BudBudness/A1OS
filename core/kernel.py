from company.orchestrator import Orchestrator
import json
import os

class Kernel:
    def __init__(self):
        self.orch = Orchestrator()
        self.registry = self.orch.registry.get_workers()

    def process_input(self, raw_message):
        # 1. Route message through CommWorker
        task = self.registry['comm'].process_message(raw_message)
        
        # 2. If valid task, dispatch to procurement
        if task and task['action'] == 'order_supplies':
            return self.registry['procurement'].process_task(task['item'], task['quantity'])
        return "Unknown intent"
