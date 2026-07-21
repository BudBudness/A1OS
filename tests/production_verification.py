import unittest
import os
import sys
sys.path.append(os.getcwd())

from main import A1OSRuntime
from apps.trading import TradingEngine
from apps.procurement import ProcurementManager
from marketplace.registry import MarketplaceRegistry
from company.orchestrator import AICompanyOrchestrator
from commercial.tenancy import CommercialPlatformManager

class TestA1OSProductionSystem(unittest.TestCase):
    def setUp(self):
        self.runtime = A1OSRuntime()
        self.runtime.bootstrap()
        self.registry = MarketplaceRegistry()
        self.commercial = CommercialPlatformManager()

    def test_end_to_end_system_pipeline(self):
        # Commercialization & Tenancy
        self.commercial.onboard_tenant("tenant_01", "ENTERPRISE")
        self.assertIn("tenant_01", self.commercial.tenants)

        # Marketplace Discovery and Installation
        self.registry.publish_to_marketplace("trading", TradingEngine)
        self.registry.publish_to_marketplace("procurement", ProcurementManager)
        
        inst_trade = self.registry.install_app("trading", self.runtime)
        inst_proc = self.registry.install_app("procurement", self.runtime)
        self.assertTrue(inst_trade)
        self.assertTrue(inst_proc)

        # AI Company Orchestration & Framework Execution v2 (Valid Transactions)
        orchestrator = AICompanyOrchestrator(self.runtime)
        valid_pipeline = [
            {"app_id": "trading", "action": "trade", "context": {"risk_factor": 0.02}},
            {"app_id": "procurement", "action": "procurement", "context": {"amount": 250000}}
        ]
        orchestrator.orchestrate_objective("Execute Low-Risk Corporate Tasks", valid_pipeline)
        
        # Governance & Policy Enforcement (Invalid Threshold Isolation)
        self.assertFalse(self.runtime.governance.validate_policy("trade", {"risk_factor": 0.08}))
        self.assertFalse(self.runtime.governance.validate_policy("procurement", {"amount": 6000000}))

        # Observability Metrics Extraction
        self.runtime.execute_app("trading", "trade", {"risk_factor": 0.09}) # Explicit block trigger
        blocked_metric = self.runtime.metrics.data.get("trading.blocked_actions", 0)
        self.assertEqual(blocked_metric, 1)

        # Hardening and Audit Trail File System Verification
        self.assertTrue(os.path.exists("deploy/audit_trail.jsonl"))
        self.assertTrue(os.path.exists("deploy/checkpoint.json"))

if __name__ == "__main__":
    unittest.main()
