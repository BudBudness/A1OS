from lib.base_provider import BaseProvider
class Provider(BaseProvider):
    def execute(self, action, payload): return f"TRADING_DOMAIN: {action} active"
