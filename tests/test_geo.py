# -*- coding: utf-8 -*-

import unittest

import numpy as np

from pyfuppes import geo


class TestGeo(unittest.TestCase):
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

    def test_haversine_dist(self):
        dist = 2887
        tol_decimalplaces = 0
        self.assertAlmostEqual(
            geo.haversine_dist(np.array((36.12, 33.94)), np.array((-86.67, -118.40))),
            dist,
            tol_decimalplaces,
        )


if __name__ == "__main__":
    unittest.main()
