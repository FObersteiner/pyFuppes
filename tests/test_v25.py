# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from pyfuppes import v25

try:
    wd = Path(__file__).parent
except NameError:
    wd = Path.cwd()
assert wd.is_dir(), "faild to obtain working directory"

src, dst = wd / "test_input", wd / "test_output"


class TestTimeconv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("\ntesting pyfuppes.v25...")

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

    def test_log_cleaner(self):
        pass


if __name__ == "__main__":
    unittest.main()
