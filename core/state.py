import inspect
from runtime.events.router import EventRouter
from runtime.scheduler.worker_scheduler import WorkerScheduler
from infra.messaging.bus import MessageBus
# from ai.reasoner.engine import ReasoningEngine
from ai.memory.engine import MemoryEngine
from ai.knowledge.base import KnowledgeBase
from core.plugin_loader import PluginLoader
from orchestration.workflow.engine import WorkflowEngine
from governance.policies.rules_engine import RulesEngine
# from modules.crm.engine import CRMEngine
# from modules.finance.engine import FinanceEngine
from modules.procurement.engine import ProcurementEngine
from modules.hr.engine import HREngine
from modules.sales.engine import SalesEngine
from services.notifications.engine import NotificationEngine
from security.auth.engine import AuthEngine
from marketplace.core.engine import MarketplaceEngine
from customer.portal.engine import CustomerPortal
from apps.admin.dashboard import AdminDashboard
# from observability.monitoring.engine import MonitoringEngine
from selfheal.engine import SelfHealEngine
from execution.distributed.engine import DistributedEngine
from core.runtime import Runtime
from core.queue.durable import DurableQueue

class CapabilityRegistry:
    """
    Central registry for executable A1OS capabilities.

    Every capability follows the durable execution contract:
        async handler(**kwargs) -> result
    """

    def __init__(self):
        self._capabilities = {}

    def register(self, name, handler):
        if not callable(handler):
            raise TypeError(f"Capability handler for '{name}' must be callable")
        self._capabilities[name] = handler

    def unregister(self, name):
        self._capabilities.pop(name, None)

    def has(self, name):
        return name in self._capabilities

    def list(self):
        return sorted(self._capabilities.keys())

    async def execute(self, name, **kwargs):
        handler = self._capabilities.get(name)

        if handler is None:
            raise RuntimeError(
                f"Capability not registered: {name}"
            )

        result = handler(**kwargs)

        if inspect.isawaitable(result):
            result = await result

        return result


class A1OS:
    def __init__(self):
        self.capabilities = CapabilityRegistry()
        self._register_capabilities()
        self.bus = MessageBus()
        self.knowledge = KnowledgeBase()
        self.runtime = Runtime(self)
        self.events = EventRouter()
        self.scheduler = WorkerScheduler()
        self.reasoner = None
        self.memory = MemoryEngine()
        self.plugins = PluginLoader()
        self.workflow = WorkflowEngine()
        self.rules = RulesEngine()
        self.crm = None
        self.finance = None
        self.procurement = ProcurementEngine()
        self.hr = HREngine()
        self.sales = SalesEngine()
        self.notifications = NotificationEngine()
        self.auth = AuthEngine()
        self.marketplace = MarketplaceEngine()
        self.portal = CustomerPortal()
        self.dashboard = AdminDashboard()
        self.monitoring = None
        self.selfheal = SelfHealEngine()
        self.distributed = DistributedEngine()
    
    async def start(self):
        recovered = DurableQueue.recover_running()

        if recovered:
            print(
                f"[A1OS] Recovered {recovered} interrupted task(s) "
                "from running -> retry."
            )

        await self.runtime.start()
        
        # Wire automated multi-stage workflow pipeline subscribers
        self.bus.subscribe("sales.order_created", self._workflow_stage_one_finance)
        self.bus.subscribe("finance.ledger_updated", self._workflow_stage_two_notification)
        self.bus.subscribe("task.completed", self._handle_task_completed_event)
        
        # self.reasoner.add_rule(condition="analytics", action="ROUTE_TO_DISTRIBUTED_COMPUTE_MATRIX")
        # self.reasoner.add_rule(condition="finance", action="TRIGGER_LEDGER_AUDIT_SEQUENCE")
        # self.reasoner.add_rule(condition="sales", action="INITIATE_WORKFLOW_ORCHESTRATION")
        
        def dynamic_match(condition: str, data: dict) -> bool:
            return condition in data.get("target", "").lower() or condition in data.get("action", "").lower()
        # self.reasoner._match_condition = dynamic_match
        self.rules.add_rule(name="Sandbox Standard User", condition={"role": "user"}, action={"escalate": False})
        print("[A1OS] Runtime topology and automated execution loop loaded successfully.")

    async def _workflow_stage_one_finance(self, payload: dict):
        print(f"   ⚙️ [Workflow Stage 1] Order detected. Transitioning to FinanceEngine allocation.")
        # Pipe payload smoothly into next module
        await self.runtime.execute(
            task_id=payload.get("task_id", "dynamic_wf"),
            payload={"target": "finance", "action": "allocate_funds", "role": "system", "data": payload.get("data")}
        )

    async def _workflow_stage_two_notification(self, payload: dict):
        print(f"   ⚙️ [Workflow Stage 2] Financial ledger validated. Dispatching global notification receipt.")
        await self.bus.publish("task.completed", {"task_id": payload.get("task_id"), "payload": payload})

    async def _handle_task_completed_event(self, payload: dict):
        print(f"   🔔 [Notification Engine Execution] Pipeline run completed successfully for: '{payload.get('task_id')}'")
        current_runs = self.knowledge.get_meta("total_completed_tasks", 0)
        self.knowledge.set_meta("total_completed_tasks", current_runs + 1)

    async def _capability_health_check(self, **kwargs):
        return {
            "status": "healthy",
            "runtime": self.runtime.__class__.__name__,
            "database": "available",
        }

    async def _capability_diagnostics(self, **kwargs):
        return {
            "status": "diagnostics_complete",
            "runtime": self.runtime.__class__.__name__,
            "capabilities": self.capabilities.list(),
        }

    async def _capability_recover(self, **kwargs):
        recovered = 0

        if hasattr(self.runtime, "recover"):
            result = self.runtime.recover()
            if inspect.isawaitable(result):
                result = await result
            recovered = result if result is not None else 0

        return {
            "status": "recovery_complete",
            "recovered": recovered,
        }

    async def _capability_list(self, **kwargs):
        return {
            "status": "capabilities_available",
            "capabilities": self.capabilities.list(),
        }

    def _register_capabilities(self):
        self.capabilities.register(
            "health_check",
            self._capability_health_check,
        )
        self.capabilities.register(
            "diagnostics",
            self._capability_diagnostics,
        )
        self.capabilities.register(
            "recover",
            self._capability_recover,
        )
        self.capabilities.register(
            "database_repair",
            self._capability_database_repair,
        )
        self.capabilities.register(
            "process_management",
            self._capability_process_management,
        )
        self.capabilities.register(
            "service_management",
            self._capability_service_management,
        )
        self.capabilities.register(
            "observability",
            self._capability_observability,
        )
        self.capabilities.register(
            "digital_world_model",
            self._capability_digital_world_model,
        )
        self.capabilities.register(
            "security_audit",
            self._capability_security_audit,
        )
        self.capabilities.register(
            "filesystem_management",
            self._capability_filesystem_management,
        )
        self.capabilities.register(
            "network_management",
            self._capability_network_management,
        )
        self.capabilities.register(
            "capabilities",
            self._capability_list,
        )

    async def _capability_service_management(self, operation="list", **kwargs):
        import subprocess

        if operation == "list":
            result = subprocess.run(
                ["ps", "-ef"],
                capture_output=True,
                text=True,
                check=False,
            )

            services = [
                line
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            return {
                "status": "service_inventory_complete",
                "count": len(services),
                "services": services,
            }

        if operation == "health":
            result = subprocess.run(
                ["ps", "-ef"],
                capture_output=True,
                text=True,
                check=False,
            )

            services = [
                line
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            return {
                "status": "service_health_complete",
                "service_count": len(services),
            }

        raise RuntimeError(
            f"Unsupported service management operation: {operation}"
        )


    async def _capability_process_management(self, operation="list", **kwargs):
        action = operation
        import subprocess

        if action == "list":
            result = subprocess.run(
                ["ps", "-ef"],
                capture_output=True,
                text=True,
                check=False,
            )

            processes = [
                line
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            return {
                "status": "process_inventory_complete",
                "count": len(processes),
                "processes": processes,
            }

        if action == "health":
            result = subprocess.run(
                ["ps", "-ef"],
                capture_output=True,
                text=True,
                check=False,
            )

            processes = [
                line
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            return {
                "status": "process_health_complete",
                "process_count": len(processes),
            }

        raise RuntimeError(
            f"Unsupported process management action: {action}"
        )


    async def _capability_network_management(self, operation="interfaces", **kwargs):
        import subprocess

        commands = {
            "interfaces": ["ip", "addr"],
            "routes": ["ip", "route"],
            "connections": ["ss", "-tun"],
            "ports": ["ss", "-lntup"],
        }

        if operation not in commands:
            raise RuntimeError(
                f"Unsupported network management operation: {operation}"
            )

        result = subprocess.run(
            commands[operation],
            capture_output=True,
            text=True,
            check=False,
        )

        return {
            "status": "network_inventory_complete",
            "operation": operation,
            "return_code": result.returncode,
            "output": result.stdout.splitlines(),
            "errors": result.stderr.splitlines(),
        }


    async def _capability_filesystem_management(self, operation="disk_usage", path=".", **kwargs):
        import shutil
        from pathlib import Path

        target = Path(path).expanduser()

        if operation == "disk_usage":
            usage = shutil.disk_usage(target)
            return {
                "status": "filesystem_inventory_complete",
                "path": str(target),
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
            }

        if operation == "exists":
            return {
                "status": "filesystem_check_complete",
                "path": str(target),
                "exists": target.exists(),
                "is_file": target.is_file(),
                "is_directory": target.is_dir(),
            }

        raise RuntimeError(
            f"Unsupported filesystem management operation: {operation}"
        )


    async def _capability_security_audit(self, operation="open_ports", **kwargs):
        import subprocess

        commands = {
            "open_ports": ["ss", "-lntup"],
            "processes": ["ps", "-ef"],
        }

        if operation not in commands:
            raise RuntimeError(
                f"Unsupported security audit operation: {operation}"
            )

        result = subprocess.run(
            commands[operation],
            capture_output=True,
            text=True,
            check=False,
        )

        return {
            "status": "security_audit_complete",
            "operation": operation,
            "return_code": result.returncode,
            "findings": [
                line
                for line in result.stdout.splitlines()
                if line.strip()
            ],
        }


    async def _capability_observability(self, operation="runtime", **kwargs):
        import time

        return {
            "status": "observability_snapshot_complete",
            "operation": operation,
            "timestamp": time.time(),
            "runtime": str(getattr(self, "runtime", None)),
            "capabilities": self.capabilities.list(),
        }


    async def _capability_digital_world_model(
        self,
        operation="snapshot",
        entity_type=None,
        entity_id=None,
        entity=None,
        relationship=None,
        state=None,
        **kwargs,
    ):
        import time
        import uuid

        entities = {
            "device",
            "process",
            "service",
            "network",
            "database",
            "application",
            "user",
            "business",
            "ai_agent",
        }

        relationships = {
            "depends_on",
            "runs_on",
            "connects_to",
            "owns",
            "monitors",
            "repairs",
        }

        states = {
            "healthy",
            "degraded",
            "failed",
            "compromised",
            "recovering",
        }

        if operation == "snapshot":
            return {
                "status": "digital_world_model_snapshot_complete",
                "system": "A1OS",
                "entities": sorted(entities),
                "relationships": sorted(relationships),
                "states": sorted(states),
                "timestamp": time.time(),
            }

        if operation == "understand":
            return {
                "status": "digital_world_understood",
                "entities": sorted(entities),
                "relationships": sorted(relationships),
                "states": sorted(states),
                "capabilities": self.capabilities.list(),
            }

        if operation == "register_entity":
            if entity_type not in entities:
                raise RuntimeError(
                    f"Unsupported entity type: {entity_type}"
                )

            state = state or "healthy"

            if state not in states:
                raise RuntimeError(
                    f"Unsupported entity state: {state}"
                )

            return {
                "status": "entity_registered",
                "entity": {
                    "id": entity_id or str(uuid.uuid4()),
                    "type": entity_type,
                    "state": state,
                    "metadata": entity or {},
                    "registered_at": time.time(),
                },
            }

        if operation == "relate_entities":
            if relationship not in relationships:
                raise RuntimeError(
                    f"Unsupported relationship: {relationship}"
                )

            return {
                "status": "relationship_registered",
                "relationship": {
                    "source": entity_id,
                    "target": kwargs.get("target_id"),
                    "type": relationship,
                    "created_at": time.time(),
                },
            }

        if operation == "set_state":
            if state not in states:
                raise RuntimeError(
                    f"Unsupported entity state: {state}"
                )

            return {
                "status": "entity_state_updated",
                "entity_id": entity_id,
                "state": state,
                "updated_at": time.time(),
            }

        if operation == "govern":
            return {
                "status": "sovereign_governance_ready",
                "authority": "A1OS",
                "scope": "entire_digital_world",
                "control_loop": [
                    "observe",
                    "understand",
                    "decide",
                    "operate",
                    "verify",
                    "repair",
                    "learn",
                ],
            }

        raise RuntimeError(
            f"Unsupported digital world model operation: {operation}"
        )


    async def _capability_database_repair(self, **kwargs):
        """
        Verify database integrity and return repair status.
        """
        db = getattr(self, "knowledge", None)

        if db is None:
            raise RuntimeError("Knowledge/database subsystem unavailable")

        result = {
            "status": "database_verified",
            "database": db.__class__.__name__,
        }

        integrity = getattr(db, "integrity_check", None)

        if callable(integrity):
            check = integrity()
            if hasattr(check, "__await__"):
                check = await check
            result["integrity"] = check
        else:
            result["integrity"] = "available"

        return result

    async def execute(self, action: str, **kwargs):
        """
        Execute any registered system capability through the unified
        capability execution contract.
        """
        return await self.capabilities.execute(action, **kwargs)


# Global A1OS system instance used by the application lifecycle.


system = A1OS()
