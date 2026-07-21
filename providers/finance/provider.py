from lib.base_provider import BaseProvider

class Provider(BaseProvider):
    def execute(self, action, payload):
        return f"FINANCE_DOMAIN_PROCESS: {action} successful"
