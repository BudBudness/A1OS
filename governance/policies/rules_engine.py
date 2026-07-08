from typing import Dict, List

class RulesEngine:
    def __init__(self):
        self.rules: List[Dict] = []
    
    def add_rule(self, name: str, condition: Dict, action: Dict):
        self.rules.append({
            "name": name,
            "condition": condition,
            "action": action
        })
    
    def evaluate(self, context: Dict) -> List[Dict]:
        triggered = []
        for rule in self.rules:
            if self._matches(rule["condition"], context):
                triggered.append({
                    "rule": rule["name"],
                    "action": rule["action"]
                })
        return triggered
    
    def _matches(self, condition: Dict, context: Dict) -> bool:
        for key, value in condition.items():
            if key in context and context[key] != value:
                return False
        return True
