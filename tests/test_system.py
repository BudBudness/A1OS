import unittest
from modules.base import BaseModule

class TestBase(unittest.TestCase):
    def test_base_init(self):
        b = BaseModule()
        self.assertIsNotNone(b.logger)

if __name__ == "__main__":
    unittest.main()
