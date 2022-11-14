# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from pyfuppes.na1001 import FFI1001 as na1001

wd = Path(__file__).parent
src, dst = wd / "test_input", wd / "test_output"


class TestNa1001(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("\ntesting na1001...")

    @classmethod
    def tearDownClass(cls):
        # to run after all tests
        pass

    def setUp(self):
        # to run before each test
        pass

    def tearDown(self):
        # to run after each test
        pass

    def test_read_valid(self):
        file = src / "valid_1001a.na"
        na = na1001(file, sep_data=" ", rmv_repeated_seps=True)
        self.assertIsNotNone(na)
        self.assertEqual(na.NV, 2)
        self.assertEqual(na.NLHEAD, 36)

    def test_invalid_read_config(self):
        file = src / "valid_1001a.na"
        with self.assertRaises(Exception):
            na1001(file, rmv_repeated_seps=False)


if __name__ == "__main__":
    unittest.main()
