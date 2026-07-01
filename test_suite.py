import unittest
import sys
import os
sys.path.append(os.path.expanduser("~/A1OS"))

from core.bus import EventBus
from core.orchestrator import Orchestrator
from core.governance import CircuitBreaker
from core.memory import MemoryManager

class TestA1OS(unittest.TestCase):
    def setUp(self):
        self.o = Orchestrator()
        self.governance = CircuitBreaker(threshold=100.0)

    def test_governance_limit(self):
        data = {'type': 'FINANCIAL_PAYOUT', 'amount': 500}
        with self.assertRaises(PermissionError):
            self.governance.validate(data['type'], data)
        print("PASS: Governance blocked over-limit payout")

    def test_memory_recording(self):
        mem = MemoryManager(db_path=":memory:")
        mem.record_decision("TEST_EVENT", {"data": "input"}, "SUCCESS")
        cursor = mem.conn.execute("SELECT * FROM episodic WHERE event_type=?", ("TEST_EVENT",))
        self.assertIsNotNone(cursor.fetchone())
        print("PASS: Memory recording successful")

    def test_event_loop(self):
        EventBus.emit("TaskRequested", {'type': 'TASK', 'goal': 'Test'})
        print("PASS: Event triggered")

if __name__ == '__main__':
    unittest.main()
