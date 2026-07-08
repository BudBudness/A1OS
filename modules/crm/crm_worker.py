from core.worker_base import BaseWorker

class CRMWorker(BaseWorker):
    def __init__(self):
        super().__init__("crm")

    def process_task(self, task):
        action = task.get("action", "retrieve")
        tenant_id = task.get("tenant_id")
        if not tenant_id:
            return {"error": "Missing tenant_id for customer data isolation"}
            
        state = self.load_state()
        tenant_space = state.setdefault(tenant_id, {"profiles": {}})

        if action == "upsert":
            customer_id = task.get("customer_id")
            profile_data = task.get("profile", {})
            if not customer_id:
                return {"error": "Missing customer_id"}
            tenant_space["profiles"][customer_id] = profile_data
            self.save_state(state)
            return {"status": "success", "customer_id": customer_id}

        elif action == "retrieve":
            return {"tenant_id": tenant_id, "profiles": tenant_space["profiles"]}

        return {"error": "Unknown CRM action"}
