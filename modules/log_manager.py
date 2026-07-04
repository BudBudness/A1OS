import datetime
import os

class LogManager:
    def __init__(self):
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f"{self.log_dir}/system.log", "a") as f:
            f.write(f"[{timestamp}] {message}\n")
