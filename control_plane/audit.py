import time
class Audit:
    def __init__(self): self.events = []
    def log(self, event_type, module): self.events.append({"time": time.time(), "event": event_type, "module": module})
