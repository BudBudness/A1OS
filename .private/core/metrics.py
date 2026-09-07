class Metrics:
    def __init__(self):
        self.data = {}

    def record(self, name, value=1, tags=None):
        if not isinstance(name, str) or not name:
            raise ValueError('metric name must be a non-empty string')

        self.data[name] = value
        return value
