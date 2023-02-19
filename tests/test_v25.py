# -*- coding: utf-8 -*-

import unittest
import shutil

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
        _ = shutil.unpack_archive(src / "v25_cleaner.zip", src / "tmp")

    @classmethod
    def tearDownClass(cls):
        # to run after all tests
        _ = shutil.rmtree(src / "tmp")

    def setUp(self):
        # to run before each test
        pass

    def tearDown(self):
        # to run after each test
        pass

    def test_log_cleaner(self):
        # run cleaner
        _ = v25.logs_cleanup(
            [src / "tmp/v25_cleaner/have"],
            verbose=True,
        )
        # have and want must now be identical, "delete" files must not exist in want
        for f_have in list((src / "tmp/v25_cleaner/have").glob("*")):
            f_want = f_have.parent.parent / "want" / f_have.name
            if f_want.name.startswith("delete"):
                self.assertFalse(f_want.is_file())
            else:
                with open(f_want, "rb") as a, open(f_have, "rb") as b:
                    self.assertEqual(
                        len(b.read()),
                        len(a.read()),
                        msg=f"{f_have.name} not identical to {f_want.name}",
                    )


if __name__ == "__main__":
    unittest.main()
