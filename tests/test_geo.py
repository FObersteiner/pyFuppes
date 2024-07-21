# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timezone

import numpy as np

from pyfuppes import geo


class TestGeo(unittest.TestCase):
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

    def test_sza(self):
        a = geo.sza(datetime(1970, 1, 1, tzinfo=timezone.utc), 42, 55)
        b = geo.sza_pysolar(datetime(1970, 1, 1, tzinfo=timezone.utc), 42, 55)
        self.assertAlmostEqual(a, b, delta=0.05)

        a = geo.sza(datetime(2013, 9, 2, 10, 47, tzinfo=timezone.utc), 10, 33)
        b = geo.sza_pysolar(datetime(2013, 9, 2, 10, 47, tzinfo=timezone.utc), 10, 33)
        self.assertAlmostEqual(a, b, delta=0.05)

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
