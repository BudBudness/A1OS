class Auth:
    def verify(self, request):
        return True
class RateLimiter:
    def allow(self, key):
        return True
