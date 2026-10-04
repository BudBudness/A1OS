import asyncio
import unittest

from ai.gateway.engine import AIEngine
from ai.reasoner.engine import Reasoner


class TestDecisionIntelligenceBoundary(unittest.TestCase):
    def test_safe_request_is_only_classified(self):
        result = Reasoner().decide(
            {"action": "inspect", "risk": "low", "authorized": True}
        )
        self.assertEqual(result["decision"], "proceed")
        self.assertFalse(result["requires_approval"])
        self.assertFalse(result["execution_authorized"])

    def test_consequential_request_requires_human_approval(self):
        result = Reasoner().decide(
            {"action": "delete", "risk": "high", "authorized": True}
        )
        self.assertEqual(result["decision"], "hold")
        self.assertTrue(result["requires_approval"])
        self.assertFalse(result["execution_authorized"])

    def test_unauthorized_request_is_rejected(self):
        result = Reasoner().decide(
            {"action": "deploy", "risk": "low", "authorized": False}
        )
        self.assertEqual(result["decision"], "reject")
        self.assertFalse(result["execution_authorized"])

    def test_ai_gateway_fails_closed_without_provider(self):
        result = asyncio.run(AIEngine().think("analyze this"))
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["execution_authorized"])

    def test_empty_prompt_is_rejected(self):
        result = asyncio.run(AIEngine().think(""))
        self.assertEqual(result["status"], "rejected")
        self.assertFalse(result["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
