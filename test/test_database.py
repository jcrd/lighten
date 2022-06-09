import os
import unittest
from datetime import time

from lightend.database import DB


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = DB("test/test.db")
        self.db.save_dict(
            {
                time(7, 30, 0): 30,
                time(8, 30, 0): 35,
                time(8, 45, 0): 45,
                time(10, 30, 0): 60,
                time(11, 30, 30): 65,
                time(11, 30, 45): 70,
                time(13, 30, 30): 85,
                time(16, 15, 15): 90,
                time(18, 18, 18): 80,
                time(19, 19, 0): 55,
                time(20, 30, 0): 40,
            }
        )

    def test_get(self):
        cases = {
            time(1, 15, 0): 40,
            time(5, 15, 0): 30,
            time(12, 30, 30): 70,
            time(14, 30, 0): 85,
            time(18, 30, 0): 80,
        }
        for d, v in cases.items():
            self.assertEqual(self.db.get(d), v)

    def tearDown(self):
        os.remove("test/test.db")
