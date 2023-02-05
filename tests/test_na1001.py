# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

import polars as pl

from pyfuppes.na1001 import FFI1001 as na1001

try:
    wd = Path(__file__).parent
except NameError:
    wd = Path.cwd()
assert wd.is_dir(), "faild to obtain working directory"

src, dst = wd / "test_input", wd / "test_output"


class TestNa1001(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        pass

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
        file = src / "validate_na/valid_1001a.na"
        na = na1001(file, sep_data=" ", rmv_repeated_seps=True)
        self.assertIsNotNone(na)
        self.assertEqual(na.NV, 2)
        self.assertEqual(na.NLHEAD, 36)
        self.assertEqual(na.HEADER.count("\n") + 1, na.NLHEAD)

        file = src / "validate_na/OM_20200304_591_CPT_MUC_V01_valid0.txt"
        na = na1001(file, sep_data="\t")
        self.assertEqual(na.HEADER.count("\n") + 1, na.NLHEAD)

    def test_invalid_read_config(self):
        file = src / "validate_na/valid_1001a.na"
        with self.assertRaises(Exception):
            na1001(file, rmv_repeated_seps=False)

    def test_validate(self):
        # cases
        # (filepath, expect_fail?)
        cases = sorted(
            (f, "invalid" in f.name) for f in (src / "validate_na").glob("*.txt")
        )
        self.assertNotEqual([], cases)
        for path, expect_fail in cases:
            if expect_fail:
                with self.assertRaises(Exception):
                    _ = na1001(path)
            else:
                result = na1001(path)
                self.assertIsNotNone(result)

    def test_poldf(self):
        file = src / "validate_na/OM_20200304_591_CPT_MUC_V01_valid0.txt"
        na = na1001(file, sep_data="\t")
        df = na.to_poldf(add_datetime=True)
        self.assertTrue(isinstance(df, pl.DataFrame))
        self.assertTrue("datetime" in df.columns)


if __name__ == "__main__":
    unittest.main()
