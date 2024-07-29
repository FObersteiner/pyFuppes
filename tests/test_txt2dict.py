# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from pyfuppes import txt2dict

try:
    wd = Path(__file__).parent
except NameError:
    wd = Path.cwd()
assert wd.is_dir(), "faild to obtain working directory"

src = wd / "test_input" / "validate_na"


class TestTimecorr(unittest.TestCase):
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

    def test_txt2dict_basic(self):
        # this just reads each line until delimiter is encountered
        d = txt2dict.txt_2_dict_basic(
            src / "OM_20200304_591_CPT_MUC_V01_valid1.txt", offset=0, delimiter=" "
        )
        self.assertListEqual(["37"], list(d.keys()))

        # correct offset and delimiter:
        d = txt2dict.txt_2_dict_basic(
            src / "OM_20200304_591_CPT_MUC_V01_valid1.txt", offset=36, delimiter="\t"
        )
        self.assertListEqual(["TimeCRef", "Özone"], list(d.keys()))

    def test_txt2dict(self):
        # invalid settings
        with self.assertRaises(ValueError):
            _ = txt2dict.txt_2_dict(src / "OM_20200304_591_CPT_MUC_V01_valid1.txt")

        d = txt2dict.txt_2_dict(
            src / "OM_20200304_591_CPT_MUC_V01_valid1.txt", colhdr_ix=36, delimiter="\t"
        )
        self.assertListEqual(["TimeCRef", "Özone"], list(d.data.keys()))
        self.assertEqual(len(d.file_hdr), 36)


if __name__ == "__main__":
    unittest.main()
