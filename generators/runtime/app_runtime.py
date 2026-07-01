from control_plane.governance.approval_pipeline import ApprovalPipeline

class AppRuntimeEngine:
    def __init__(self, root_dir, control_plane):
        self.root_dir = root_dir
        self.control_plane = control_plane
        self.approvals = ApprovalPipeline()

    async def execute_intent(self, app_id, intent):
        # 1. Audit Policy: Every intent is logged
        await self.control_plane.bus.emit("GOVERNANCE_AUDIT", {
            "app": app_id, 
            "action": intent.get("syscall")
        })
        
        # 2. Execution Logic
        if intent.get("requires_approval", False):
            req_id = self.approvals.request(app_id, intent)
            if req_id is None:
                return {"status": "EXECUTED_VIA_AUTO_APPROVAL"}
            return {"status": "PENDING_APPROVAL", "id": req_id}
        return {"status": "EXECUTED"}
