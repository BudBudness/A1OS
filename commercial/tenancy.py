from typing import Dict, Any

class CommercialPlatformManager:
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}

    def onboard_tenant(self, tenant_id: str, plan: str):
        self.tenants[tenant_id] = {"plan": plan, "status": "ACTIVE", "billing_cycle": "MONTHLY"}
