import time

class RateLimiter:
    def __init__(self, limit=5, window=60):
        self.limit = limit
        self.window = window
        self.calls = []

    def check(self):
        now = time.time()
        self.calls = [c for c in self.calls if now - c < self.window]
        if len(self.calls) >= self.limit:
            raise PermissionError("Rate limit exceeded")
        self.calls.append(now)
        return True
