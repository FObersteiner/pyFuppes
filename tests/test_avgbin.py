# -*- coding: utf-8 -*-

import unittest

import numpy as np

from pyfuppes import avgbinmap


class TestAvgbinmap(unittest.TestCase):
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

    def test_mean_angle(self):
        for angles, mean in zip([[350, 10], [90, 180, 270, 360], [10, 20, 30]], (0, -90, 20)):
            self.assertAlmostEqual(avgbinmap.mean_angle(np.array(angles)), mean)
            self.assertAlmostEqual(avgbinmap.mean_angle_sc(np.array(angles)), mean)
            self.assertAlmostEqual(avgbinmap.mean_angle_numba(np.array(angles)), mean)

    def test_mean_dayfrac(self):
        for angles, mean in zip([[350, 10], [90, 180, 270, 360], [10, 20, 30]], (0, 270, 20)):
            self.assertAlmostEqual(
                avgbinmap.mean_day_frac(np.array(angles) / 360, use_numba=False),
                mean / 360,
            )
            self.assertAlmostEqual(
                avgbinmap.mean_day_frac(np.array(angles) / 360, use_numba=True),
                mean / 360,
            )

    def test_bin_t_10s(self):
        # TODO
        pass

    def test_bin_y_of_t(self):
        # TODO
        pass

    def test_bin_by_pdresample(self):
        # TODO
        pass

    def test_bin_by_npreduceat(self):
        # TODO
        pass

    def test_moving_avg(self):
        # TODO
        pass

    def test_np_mvg_avg(self):
        # TODO
        pass

    def test_sp_mvg_avg(self):
        # TODO
        pass

    def test_map_dependent(self):
        # first missing
        xref = np.array([1, 2, 3], dtype=int)
        xcmp = np.array([2, 3, 4], dtype=int)
        vcmp = np.array([1, 2, 3], dtype=float)
        tgt = np.array([np.nan, 1, 2], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt)))

        # last missing
        xref = np.array([1, 2, 3], dtype=int)
        xcmp = np.array([0, 1, 2], dtype=int)
        vcmp = np.array([1, 2, 3], dtype=float)
        tgt = np.array([2, 3, np.nan], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt)))

        # gap
        xref = np.array([1, 2, 3, 4], dtype=int)
        xcmp = np.array([1, 4, 5, 6], dtype=int)
        vcmp = np.array([1, 2, 3, 4], dtype=float)
        tgt = np.array([1, np.nan, np.nan, 2], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt)))

        # missing elements in cmp
        xref = np.array([1, 2, 3, 4], dtype=int)
        xcmp = np.array([1, 4, 5], dtype=int)
        vcmp = np.array([1, 2, 3], dtype=float)
        tgt = np.array([1, np.nan, np.nan, 2], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt)))

        # missing elements in ref
        xref = np.array([1, 2, 3], dtype=int)
        xcmp = np.array([1, 4, 5, 6], dtype=int)
        vcmp = np.array([1, 2, 3, 4], dtype=float)
        tgt = np.array([1, np.nan, np.nan], dtype=float)
        test = avgbinmap.map_dependent(xref, xcmp, vcmp)
        self.assertTrue(all(a == b if np.isfinite(b) else np.isnan(a) for a, b in zip(test, tgt)))

    def test_pd_DataFrame_ip(self):
        # TODO
        pass

    def test_pd_Series_ip(self):
        # TODO
        pass

    def test_calc_shift(self):
        have = np.array([1.2, 2.1, 2.5, 4.1, 5.3, 6.0, 7.1, 7.9, 9.0, 10.6], dtype=float)
        want = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
        shift = avgbinmap.calc_shift(have, step=1, lower_bound=-2, upper_bound=3)
        self.assertTrue(np.isclose(have + shift, want).all())
        # TODO: add more tests ?


if __name__ == "__main__":
    unittest.main()
