class ApprovalPipeline:
    def __init__(self):
        self.pending = {}
        self.counter = 0

    def request(self, app_id, intent):
        # Risk assessment logic: Low-risk if not modifying 'main' or 'prod'
        is_high_risk = any(kw in intent.get("target", "") for kw in ["main", "prod", "financial"])
        
        if not is_high_risk:
            print(f"✅ [GOVERNANCE] Low-risk task from {app_id}. Auto-approving.")
            return None # Return None to indicate no approval needed
            
        req_id = self.counter
        self.pending[req_id] = intent
        self.counter += 1
        return req_id

    def approve(self, req_id):
        return self.pending.pop(req_id, None)
