import os
import psutil

class Monitor:
    @staticmethod
    def get_stats():
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent
        }
