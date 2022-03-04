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
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([2, 3, 4, 5, 6, 7], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result["t_corr"], r).all())

        t = np.array([-2, -1, 0, 1, 2, 3], dtype=np.float32)
        r = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result["t_corr"], r).all())

        # changed order
        order = 3
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([2, 3, 4, 5, 6, 7], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result["t_corr"], r).all())

        # inclination only
        order = 1
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([1, 3, 5, 7, 9, 11], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result["t_corr"], r).all())

        # inclination + offset
        order = 1
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([2.0, 3.5, 5.0, 6.5, 8.0, 9.5], dtype=np.float32)
        result = timecorr.time_correction(t, r, order)
        self.assertTrue(np.isclose(result["t_corr"], r).all())

    def test_xcorr_timelag(self):
        # signal with peak
        t = np.linspace(0, 250, 250)
        f = 10 * np.exp(-((t - 90) ** 2) / 8) + np.random.randn(250) + 99
        g = 10 * np.exp(-((t - 180) ** 2) / 8) + np.random.randn(250) + 41
        lag = timecorr.xcorr_timelag(t, f, t, g, show_plots=False)
        # print(l, 90)
        self.assertTrue(abs(lag - 90) < (90 * 0.02)
                        )  # shift is 90... expect within 2%

        # Sawtooth wave
        # https://stackoverflow.com/questions/4688715/find-time-shift-between-two-similar-waveforms
        f = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0, 1,
                     2, 3, 4, 3, 2, 1, 0, 0, 0, 0, 0])
        g = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4, 3,
                     2, 1, 0, 1, 2, 3, 4, 3, 2, 1, 0])
        t = np.arange(f.size)
        lag = timecorr.xcorr_timelag(t, f, t, g, show_plots=False)
        # print(l, 4)
        # shift is 4... expect within 10%
        self.assertTrue(abs(lag - 4) < (4 * 0.1))

        # sine waves with noise
        # https://stackoverflow.com/questions/41492882/find-time-shift-of-two-signals-using-cross-correlation
        to_freq = 50
        data = np.linspace(0, 2 * np.pi, to_freq)
        data = np.tile(np.sin(data), 5)
        data += np.random.normal(0, 5, data.shape)
        f, g = data[to_freq: 4 * to_freq], data[: 3 * to_freq]
        t = np.arange(f.size)
        lag = timecorr.xcorr_timelag(t, f, t, g, show_plots=False)
        # print(l, to_freq)
        self.assertTrue(
            abs(lag - to_freq) < (to_freq * 0.02)
        )  # shift is to_freq... expect within 2%

        # more waves
        # https://stackoverflow.com/questions/13826290/estimating-small-time-shift-between-two-time-series
        shift = -3
        x0 = np.linspace(0, 10, 100)
        x1 = 1 * x0 + shift
        f = sum([np.sin(2 * np.pi * i * x0 / 10) for i in range(1, 5)])
        g = sum([np.sin(2 * np.pi * i * x1 / 10) for i in range(1, 5)])
        lag = timecorr.xcorr_timelag(
            x0, f, x0, g, xrange=(x0.min(), x1.max()), show_plots=False
        )
        # print(l, shift*-1)
        # shift is 90... expect within 2%
        self.assertTrue(abs(lag - 3) < (3 * 0.02))


if __name__ == "__main__":
    unittest.main()
