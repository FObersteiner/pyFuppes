import unittest

import numpy as np

from pyfuppes import timecorr



class TestTimeconv(unittest.TestCase):

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

    def test_time_correction(self):
        # offset only
        order = 1
        t = np.array([1,2,3,4,5,6], dtype=np.float32)
        r = np.array([2,3,4,5,6,7], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result['t_corr'], r).all())

        t = np.array([-2,-1,0,1,2,3], dtype=np.float32)
        r = np.array([1,2,3,4,5,6], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result['t_corr'], r).all())

        # changed order
        order = 3
        t = np.array([1,2,3,4,5,6], dtype=np.float32)
        r = np.array([2,3,4,5,6,7], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result['t_corr'], r).all())

        # inclination only
        order = 1
        t = np.array([1,2,3,4,5,6], dtype=np.float32)
        r = np.array([1,3,5,7,9,11], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result['t_corr'], r).all())

        # inclination + offset
        order = 1
        t = np.array([1,2,3,4,5,6], dtype=np.float32)
        r = np.array([2.0, 3.5, 5.0, 6.5, 8.0, 9.5], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result['t_corr'], r).all())



if __name__ == '__main__':
    unittest.main()
