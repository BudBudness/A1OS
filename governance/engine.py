from typing import Dict

class GovernanceEngine:
    def validate(self, report: Dict) -> bool:
        return report.get("status") == "stable"

    def authorize_optimization(self, report: Dict) -> str:
        if report.get("metrics", {}).get("cpu", 0) > 90:
            return "emergency_shutdown"
        return "optimize_resources"
