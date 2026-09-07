class ManualApprovalGate:
    def request_approval(self, task_id, decision):
        print(f"\n[MANUAL APPROVAL REQUIRED] Task: {task_id}")
        print(f"Action: {decision.get('action')}")
        print(f"Data: {decision}")
        
        user_input = input("Approve task? (Y/N): ").strip().upper()
        
        if user_input == 'Y':
            print(f"[APPROVED] Task {task_id} proceeding.")
            return True
        else:
            print(f"[DENIED] Task {task_id} rejected.")
            return False
