import os
# import None (disabled on Android)

class Monitor:
    @staticmethod
    def get_stats():
        return {
            "cpu": None.cpu_percent(),
            "memory": None.virtual_memory().percent
        }
