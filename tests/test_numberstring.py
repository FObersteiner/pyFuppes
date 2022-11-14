# -*- coding: utf-8 -*-

import unittest

from pyfuppes import numberstring


class TestNumberstring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("\ntesting pyfuppes.numberstring...")

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

    def test_NumStr(self):
        valid = [
            "45",
            "45.",
            "3E5",
            "4E+5",
            "3E-3",
            "2.345E+7",
            "-7",
            "-45.3",
            "-3.4E3",
            " 12 ",
            "8.8E1",
            "+5.3",
            "+4.",
            "+10",
            "+2.3E121",
            "+4e-3",
            "-204E-9668",
            ".7",
            "+.7",
        ]
        for s in valid:
            result = numberstring.NumStr().analyse_format(s)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)

        invalid = ["tesT", "Test45", "7,7E2", "204-100", "."]
        for s in invalid:
            with self.assertRaises(TypeError):
                numberstring.NumStr().analyse_format(s)

    def test_dec2str_stripped(self):
        NUMBERS = [0.010701]
        self.assertEqual(
            "0.011",
            numberstring.dec2str_stripped(NUMBERS, dec_places=3, strip="right")[0],
        )
        self.assertEqual(
            ".011",
            numberstring.dec2str_stripped(NUMBERS, dec_places=3, strip="left")[0],
        )
        self.assertEqual(
            ".011",
            numberstring.dec2str_stripped(NUMBERS, dec_places=3, strip="both")[0],
        )

        NUMBERS = [1.0, 3.44532, 0.12011]
        self.assertEqual(
            ["1.", "3.445", "0.12"],
            numberstring.dec2str_stripped(NUMBERS, dec_places=3, strip="right"),
        )
        self.assertEqual(
            ["1.000", "3.445", ".120"],
            numberstring.dec2str_stripped(NUMBERS, dec_places=3, strip="left"),
        )
        self.assertEqual(
            ["1.", "3.445", ".12"],
            numberstring.dec2str_stripped(NUMBERS, dec_places=3, strip="both"),
        )


if __name__ == "__main__":
    unittest.main()
