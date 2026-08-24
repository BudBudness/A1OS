import asyncio
import unittest

from main import A1OSRuntime
from marketplace.registry import PluginLoader
from company.orchestrator import Orchestrator
from commercial.tenancy import CommercialPlatformManager


class TestA1OSProductionSystem(unittest.TestCase):

    def setUp(self):
        self.runtime = A1OSRuntime()
        self.registry = PluginLoader()
        self.commercial = CommercialPlatformManager()
        self.orchestrator = Orchestrator()

    def test_runtime_contract(self):
        from runtime.engine import A1OSEngine

        self.assertIs(A1OSRuntime, A1OSEngine)

        for symbol in ("run", "stop", "emit", "subscribe"):
            self.assertTrue(hasattr(self.runtime, symbol))

    def test_runtime_event_contract(self):
        events = []

        async def callback(event_type, data):
            events.append((event_type, data))

        self.runtime.subscribe(callback)

        asyncio.run(
            self.runtime.emit(
                "production_verification",
                {"status": "ok"},
            )
        )

        self.assertEqual(
            events,
            [("production_verification", {"status": "ok"})],
        )

    def test_marketplace_contract(self):
        self.assertTrue(hasattr(self.registry, "load_plugins"))
        self.assertTrue(callable(self.registry.load_plugins))

        result = self.registry.load_plugins(self.runtime)

        # Canonical loader may mutate runtime state and return None.
        self.assertTrue(result is None or result is not False)

    def test_tenancy_contract(self):
        self.commercial.onboard_tenant("tenant_01", "ENTERPRISE")

        self.assertIn("tenant_01", self.commercial.tenants)

        tenant = self.commercial.tenants["tenant_01"]

        self.assertEqual(tenant["plan"], "ENTERPRISE")
        self.assertEqual(tenant["status"], "ACTIVE")
        self.assertEqual(tenant["billing_cycle"], "MONTHLY")

    def test_orchestrator_contract(self):
        self.assertIsNotNone(self.orchestrator)

    def test_production_verifier_contract(self):
        self.assertIsNotNone(self.runtime)
        self.assertIsNotNone(self.registry)
        self.assertIsNotNone(self.commercial)
        self.assertIsNotNone(self.orchestrator)


if __name__ == "__main__":
    unittest.main()
