"""Governed orchestration boundary: reason -> plan -> independently authorize -> execute."""
import inspect
from typing import Any, Awaitable, Callable, Dict, Optional, Union
from ai.planner.engine import Planner
from ai.reasoner.engine import Reasoner
Executor = Callable[[Dict[str, Any], Dict[str, Any]], Union[Any, Awaitable[Any]]]
class Orchestrator:
    def __init__(self, reasoner: Optional[Reasoner]=None, planner: Optional[Planner]=None): self.reasoner=reasoner or Reasoner(); self.planner=planner or Planner()
    def prepare(self, request: Dict[str, Any]) -> Dict[str, Any]:
        decision=self.reasoner.decide(request); plan=self.planner.plan(request,decision); return {"decision":decision,"plan":plan,"execution_authorized":False}
    async def execute(self, request: Dict[str, Any], authorization: Dict[str, Any], executor: Executor) -> Dict[str, Any]:
        prepared=self.prepare(request); decision=prepared["decision"]; plan=prepared["plan"]
        if plan.get("status")!="planned": return self._blocked("plan_not_admitted",prepared)
        if not isinstance(authorization,dict) or authorization.get("approved") is not True: return self._blocked("explicit_authorization_required",prepared)
        provenance=authorization.get("provenance")
        if not isinstance(provenance,dict) or not provenance: return self._blocked("authorization_provenance_required",prepared)
        if decision.get("execution_authorized") is not False: return self._blocked("decision_authorization_boundary_violation",prepared)
        if not callable(executor): return self._blocked("executor_required",prepared)
        result=executor(plan,provenance)
        if inspect.isawaitable(result): result=await result
        return {"status":"executed","decision":decision,"plan":plan,"authorization":{"approved":True,"provenance":provenance},"result":result,"execution_authorized":True}
    @staticmethod
    def _blocked(reason,prepared): return {"status":"blocked","reason":reason,"decision":prepared["decision"],"plan":prepared["plan"],"execution_authorized":False}
