import time

class SovereignJobScheduler:
    def __init__(self):
        self.queue = []
    def defer_task(self, name, delay_sec):
        execution_epoch = time.time() + delay_sec
        self.queue.append({"job": name, "target_epoch": execution_epoch})
        return execution_epoch
