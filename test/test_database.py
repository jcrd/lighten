import os
import unittest

from lightend.database import DB


class TestDatabase(unittest.TestCase):
    def setUp(self):
        save_fidelity = 5
        self.db = DB("test/test.db", save_fidelity)
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
        self.db.save(44, 75)

    def test_get(self):
        cases = {
            10: 35,
            33: 65,
            45: 75,
            70: None,
        }
        max_deviation = 10

        for k, v in cases.items():
            self.assertEqual(self.db.get(k, max_deviation), v)

    def tearDown(self):
        os.remove("test/test.db")
