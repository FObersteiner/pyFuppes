# -*- coding: utf-8 -*-

import unittest

import numpy as np

from pyfuppes import filters


class TestFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("\ntesting pyfuppes.filters...")

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

    def test_mask_repeated(self):
        arr = np.array([1, 2, 3, 3, 3, 4, 5, 5])
        #                           |-> nok
        have = filters.mask_repeated(arr, 2)
        want = np.array([True, True, True, True, False, True, True, True])
        self.assertTrue((have == want).all())

    def test_mask_repeated_nb(self):
        arr = np.array([1, 2, 3, 3, 3, 4, 5, 5])
        #                           |-> nok
        have = filters.mask_repeated_nb(arr, 2)
        want = np.array([True, True, True, True, False, True, True, True])
        self.assertTrue((have == want).all())

    def test_mask_jumps(self):
        arr = np.array([1, 2, 3, 7, 3, 4, 5, 5])
        #                        |-> nok
        have = filters.mask_jumps(arr, 3, 1, abs_delta=False)
        want = np.array([True, True, True, False, True, True, True, True])
        self.assertTrue((have == want).all())
        # changing lookahead must not change result here:
        have = filters.mask_jumps(arr, 3, 2, abs_delta=False)
        want = np.array([True, True, True, False, True, True, True, True])
        self.assertTrue((have == want).all())

        arr = np.array([1, 2, 3, -7, 3, 4, 5, 5])
        #                            |-> nok
        have = filters.mask_jumps(arr, 3, 1, abs_delta=False)
        want = np.array([True, True, True, True, False, True, True, True])
        self.assertTrue((have == want).all())

        arr = np.array([1, 2, 3, -7, 3, 4, 5, 5])
        #                         |-> nok
        have = filters.mask_jumps(arr, 3, 1, abs_delta=True)
        want = np.array([True, True, True, False, True, True, True, True])
        self.assertTrue((have == want).all())

        arr = np.array([1, 2, 3, 8, 7, 4, 5, 5])
        #                        |--|-> nok
        have = filters.mask_jumps(arr, 3, 2, abs_delta=False)
        want = np.array([True, True, True, False, False, True, True, True])
        self.assertTrue((have == want).all())

        arr = np.array([1, 2, 3, -8, 7, 4, 5, 5])
        #                        |--|-> nok
        have = filters.mask_jumps(arr, 3, 2, abs_delta=True)
        want = np.array([True, True, True, False, False, True, True, True])
        self.assertTrue((have == want).all())

        arr = np.array([1, 2, 3, 8, -7, 4, 5, 5])
        #                        |--|-> nok
        have = filters.mask_jumps(arr, 3, 2, abs_delta=True)
        want = np.array([True, True, True, False, False, True, True, True])
        self.assertTrue((have == want).all())

    def test_filter_jumps(self):
        # TODO
        pass

    def test_filter_jumps_np(self):
        # TODO
        pass

    def test_extend_mask(self):
        m = np.array([False, False, True, False, False])
        have = filters.extend_mask(m, 0)  # n = 0 has no effect
        want = np.array([False, False, True, False, False])
        self.assertTrue((have == want).all())

        have = filters.extend_mask(m, 1)  # one 'True' inserted to the right
        want = np.array([False, False, True, True, False])
        self.assertTrue((have == want).all())

        have = filters.extend_mask(m, 2)  # another 'True' inserted to the left
        want = np.array([False, True, True, True, False])
        self.assertTrue((have == want).all())

        # edge
        m = np.array([False, False, False, False, True])
        have = filters.extend_mask(m, 1)  # n = 1 has no effect here, no element to the right
        want = np.array([False, False, False, False, True])
        self.assertTrue((have == want).all())

        have = filters.extend_mask(m, 2)  # n = 2 gives one 'True' to the left
        want = np.array([False, False, False, True, True])
        self.assertTrue((have == want).all())

        have = filters.extend_mask(m, 3)  # n = 3 gives same result as n = 2
        want = np.array([False, False, False, True, True])
        self.assertTrue((have == want).all())

        m = np.array(
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
            ]
        )
        have = filters.extend_mask(m, 5)
        want = np.array(
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                True,
                True,
                True,
                True,
                True,
            ]
        )
        self.assertTrue((have == want).all())

    def test_filter_lof(self):
        with self.assertRaises(Exception) as context:
            _ = filters.simple_1d_lof(np.array([np.nan]), 15, 1.5)
        self.assertTrue("can only use all-finite values in 'var'" in str(context.exception))

        with self.assertRaises(Exception) as context:
            _ = filters.simple_1d_lof(np.array([[1, 1], [2, 2]]), 15, 1.5)
        self.assertTrue("can only work with 1D data" in str(context.exception))

        rng = np.random.default_rng()
        data = rng.standard_normal(10000)
        n_outliers = 20

        m = np.sort(rng.choice(data.shape[0], size=n_outliers, replace=False))
        pos_neg = np.random.choice([True, False], size=n_outliers)

        out = np.absolute(np.min(data) - np.max(data)) * 3
        data[m[pos_neg]] = out
        data[m[~pos_neg]] = out * -1

        mask = filters.simple_1d_lof(data, 15, 1.5)
        self.assertEqual(
            m.shape[0], np.nonzero(mask)[0].shape[0], "lof must find prescribed outliers"
        )
        self.assertTrue((m == np.nonzero(mask)[0]).all(), "lof must find prescribed outliers")

        mask = filters.simple_1d_lof(data, 15, 1.5, mode="positive")
        self.assertEqual(
            m[pos_neg].shape[0], np.nonzero(mask)[0].shape[0], "lof must find prescribed outliers"
        )
        self.assertTrue(
            (m[pos_neg] == np.nonzero(mask)[0]).all(), "lof must find prescribed outliers"
        )

        mask = filters.simple_1d_lof(data, 15, 1.5, mode="negative")
        self.assertEqual(
            m[~pos_neg].shape[0], np.nonzero(mask)[0].shape[0], "lof must find prescribed outliers"
        )
        self.assertTrue(
            (m[~pos_neg] == np.nonzero(mask)[0]).all(), "lof must find prescribed outliers"
        )


if __name__ == "__main__":
    unittest.main()
