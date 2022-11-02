import unittest

import numpy as np

from pyfuppes import avgbinmap


class TestTimeconv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("\ntesting pyfuppes.avgbin...")

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

    def test_map_dependent(self):
        # first missing
        xref = np.array([1, 2, 3], dtype=int)
        xcmp = np.array([2, 3, 4], dtype=int)
        vcmp = np.array([1, 2, 3], dtype=float)
        tgt = np.array([np.nan, 1, 2], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(
            all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt))
        )

        # last missing
        xref = np.array([1, 2, 3], dtype=int)
        xcmp = np.array([0, 1, 2], dtype=int)
        vcmp = np.array([1, 2, 3], dtype=float)
        tgt = np.array([2, 3, np.nan], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(
            all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt))
        )

        # gap
        xref = np.array([1, 2, 3, 4], dtype=int)
        xcmp = np.array([1, 4, 5, 6], dtype=int)
        vcmp = np.array([1, 2, 3, 4], dtype=float)
        tgt = np.array([1, np.nan, np.nan, 2], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(
            all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt))
        )

        # missing elements in cmp
        xref = np.array([1, 2, 3, 4], dtype=int)
        xcmp = np.array([1, 4, 5], dtype=int)
        vcmp = np.array([1, 2, 3], dtype=float)
        tgt = np.array([1, np.nan, np.nan, 2], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(
            all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt))
        )

        # missing elements in ref
        xref = np.array([1, 2, 3], dtype=int)
        xcmp = np.array([1, 4, 5, 6], dtype=int)
        vcmp = np.array([1, 2, 3, 4], dtype=float)
        tgt = np.array([1, np.nan, np.nan], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(
            all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt))
        )


if __name__ == "__main__":
    unittest.main()
