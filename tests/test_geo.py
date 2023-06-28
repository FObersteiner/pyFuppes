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
        lyon = (45.7597, 4.8422)
        paris = (48.8567, 2.3508)
        dist = 392.2172595594006
        tol_decimalplaces = 2
        self.assertAlmostEqual(
            geo.haversine_dist(
                np.array([lyon[0], paris[0]]), np.array([lyon[1], paris[1]])
            ),
            dist,
            tol_decimalplaces,
        )


if __name__ == "__main__":
    unittest.main()
