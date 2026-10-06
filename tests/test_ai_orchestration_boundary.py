import asyncio
import unittest
from ai.orchestration.engine import Orchestrator
class TestOrchestrationBoundary(unittest.TestCase):
    def setUp(self): self.o=Orchestrator()
    def test_prepare_never_authorizes(self):
        r=self.o.prepare({"action":"inspect","target":"system","risk":"low","authorized":True}); self.assertEqual(r["decision"]["decision"],"proceed"); self.assertEqual(r["plan"]["status"],"planned"); self.assertFalse(r["execution_authorized"])
    def test_high_risk_never_reaches_executor(self):
        called=[]; r=asyncio.run(self.o.execute({"action":"delete","risk":"high","authorized":True},{"approved":True,"provenance":{"actor":"owner"}},lambda p,v: called.append(1))); self.assertEqual(r["reason"],"plan_not_admitted"); self.assertFalse(called)
    def test_missing_authorization_blocks_executor(self):
        called=[]; r=asyncio.run(self.o.execute({"action":"inspect","risk":"low","authorized":True},{},lambda p,v: called.append(1))); self.assertEqual(r["reason"],"explicit_authorization_required"); self.assertFalse(called)
    def test_authorized_plan_reaches_executor_with_provenance(self):
        captured={}; r=asyncio.run(self.o.execute({"action":"inspect","risk":"low","authorized":True},{"approved":True,"provenance":{"actor":"owner"}},lambda p,v: captured.update(plan=p,prov=v) or {"ok":True})); self.assertEqual(r["status"],"executed"); self.assertTrue(r["execution_authorized"]); self.assertEqual(captured["prov"]["actor"],"owner")
    def test_approval_without_provenance_blocks(self):
        called=[]; r=asyncio.run(self.o.execute({"action":"inspect","risk":"low","authorized":True},{"approved":True},lambda p,v: called.append(1))); self.assertEqual(r["reason"],"authorization_provenance_required"); self.assertFalse(called)
if __name__=="__main__": unittest.main()
