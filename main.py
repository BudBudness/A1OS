
import sys
import time
from governance.engine import GovernanceEngine
from observability.logging.core import Logger, MetricsCollector
from apps.base import BaseApp

class A1OSRuntime:
    def __init__(self):
        self.logger = Logger()
        self.metrics = MetricsCollector()
        self.governance = GovernanceEngine()
        self.apps = {}

    def register_app(self, app_id: str, app_instance: BaseApp):
        self.apps[app_id] = app_instance
        self.logger.log("INFO", f"Registered application context: {app_id}")

    def execute_app(self, app_id: str, action: str, context: dict):
        if app_id not in self.apps:
            self.logger.log("ERROR", f"Application {app_id} target not found.")
            return

        self.logger.log("INFO", f"Evaluating governance compliance for {app_id} -> {action}")
        start_time = time.time()
        
        if not self.governance.validate_policy(action, context):
            self.governance.log_audit_trail("POLICY_BLOCKED", {"msg": f"Governance policy violation blocked execution of {action} for {app_id}")
            self.metrics.record(f"{app_id}.blocked_actions", 1)
            self.governance.log_audit_trail("POLICY_BLOCKED", {"app_id": app_id, "action": action, "context": context})
            return

        try:
            self.logger.log("INFO", f"Invoking application execution pipeline: {app_id}")
            self.apps[app_id].run(action=action, context=context)
            
            duration = time.time() - start_time
            self.metrics.record(f"{app_id}.execution_time_ms", duration * 1000)
            self.metrics.record(f"{app_id}.execution_success", 1)
            self.governance.log_audit_trail("EXECUTION_SUCCESS", {"app_id": app_id, "action": action})
            
        except Exception as e:
            self.logger.log("CRITICAL", f"Runtime execution failure in module {app_id}: {str(e)}")
            self.metrics.record(f"{app_id}.execution_failure", 1)
            self.governance.log_audit_trail("EXECUTION_FAILURE", {"app_id": app_id, "error": str(e)})

    def bootstrap(self):
        self.logger.log("INFO", "A1OS Micro-Kernel bootstrap sequence initiated successfully.")

if __name__ == "__main__":
    runtime = A1OSRuntime()
    runtime.bootstrap()

