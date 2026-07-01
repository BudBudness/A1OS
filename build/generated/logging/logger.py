import time

class StructuredLogger:
    def __init__(self, subsystem_name="core"):
        self.subsystem = subsystem_name

    def log(self, level, message, **kwargs):
        entry = {
            "time": time.time(),
            "level": level.upper(),
            "subsystem": self.subsystem,
            "message": message,
            **kwargs
        }
        print(f"[{entry['level']}] {self.subsystem}: {message} -- Context: {kwargs}")
        return entry