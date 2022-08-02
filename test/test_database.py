import os
import unittest

from lightend.database import DB


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = DB("test/test.db")
        self.db.save_dict(
            {
                1: 30,
                10: 35,
                20: 45,
                30: 60,
                35: 65,
                40: 70,
                90: 85,
                100: 90,
            }
        )

    def test_get(self):
        cases = {
            10: 35,
            33: 65,
            45: 70,
            70: False,
        }
        max_deviation = 10

        for k, v in cases.items():
            self.assertEqual(self.db.get(k, max_deviation), v)

    def tearDown(self):
        os.remove("test/test.db")
