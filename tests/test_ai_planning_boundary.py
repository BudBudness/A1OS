import unittest

from ai.planner.engine import Planner


class TestPlanningBoundary(unittest.TestCase):
    def setUp(self):
        self.planner = Planner()

    def test_proceeding_decision_creates_explicit_plan(self):
        result = self.planner.plan(
            {"action": "inspect", "target": "system"},
            {"decision": "proceed", "requires_approval": False, "execution_authorized": False},
        )
        self.assertEqual(result["status"], "planned")
        self.assertEqual(result["steps"][0]["sequence"], 1)
        self.assertEqual(result["steps"][0]["action"], "inspect")
        self.assertFalse(result["execution_authorized"])

    def test_hold_decision_cannot_create_plan(self):
        result = self.planner.plan(
            {"action": "delete"},
            {"decision": "hold", "requires_approval": True, "execution_authorized": False},
        )
        self.assertEqual(result["status"], "held")
        self.assertEqual(result["reason"], "decision_not_proceeding")
        self.assertFalse(result["execution_authorized"])

    def test_authorization_cannot_be_granted_by_planner(self):
        result = self.planner.plan(
            {"action": "deploy"},
            {"decision": "proceed", "requires_approval": False, "execution_authorized": True},
        )
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "authorization_boundary_violation")

    def test_missing_action_is_rejected(self):
        result = self.planner.plan(
            {},
            {"decision": "proceed", "requires_approval": False, "execution_authorized": False},
        )
        self.assertEqual(result["status"], "rejected")
        self.assertFalse(result["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
