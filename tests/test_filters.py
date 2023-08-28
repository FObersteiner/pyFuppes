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
        have = filters.extend_mask(m, 1)  # n = 1 has no effect
        want = np.array([False, False, True, False, False])
        self.assertTrue((have == want).all())

        have = filters.extend_mask(m, 2)  # one 'True' inserted to the right
        want = np.array([False, False, True, True, False])
        self.assertTrue((have == want).all())

        have = filters.extend_mask(m, 3)  # another 'True' inserted to the left
        want = np.array([False, True, True, True, False])
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
        have = filters.extend_mask(m, 6)
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


if __name__ == "__main__":
    unittest.main()
