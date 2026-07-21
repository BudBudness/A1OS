from typing import List, Dict

class SelfHealEngine:
    def __init__(self):
        self.recovery_actions: List[Dict] = []
        self.diagnostics: List[Dict] = []
    
    def add_recovery_action(self, condition: str, action: str):
        self.recovery_actions.append({
            "condition": condition,
            "action": action
        })
    
    def detect_issues(self) -> List[Dict]:
        return []
    
    def recover(self, issue: Dict) -> bool:
        for action in self.recovery_actions:
            if self._matches(action["condition"], issue):
                return True
        return False
    
    def _matches(self, condition: str, issue: Dict) -> bool:
        return condition in issue.get("type", "")
