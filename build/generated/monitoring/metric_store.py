import time

class InMemoryMetricStore:
    def __init__(self, max_capacity=100):
        self.max_capacity = max_capacity
        self._buffer = []

    def append_metric(self, name, value):
        point = {"name": name, "value": value, "time": time.time()}
        self._buffer.append(point)
        if len(self._buffer) > self.max_capacity:
            self._buffer.pop(0)
            
    def get_metrics_by_name(self, name):
        return [p for p in self._buffer if p["name"] == name]