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

class A1OS:
    def __init__(self):
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

system = A1OS()
