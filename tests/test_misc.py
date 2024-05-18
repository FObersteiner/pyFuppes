# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from pyfuppes.misc import clean_path


class TestTimecorr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("\ntesting pyfuppes.timecorr...")

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

    def test_pathcleaner(self):
        p = "$HOME"
        clean_p = clean_path(p)
        self.assertEqual(clean_p.as_posix(), Path().home().as_posix())
        p = "~"
        clean_p = clean_path(p)
        self.assertEqual(clean_p.as_posix(), Path().home().as_posix())
        p = "$HOME/a_directory"
        clean_p = clean_path(p)
        self.assertEqual(clean_p.as_posix(), (Path().home() / "a_directory").as_posix())


if __name__ == "__main__":
    unittest.main()
