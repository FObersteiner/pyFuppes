# -*- coding: utf-8 -*-

import unittest

import numpy as np
import polars as pl
from polars.testing import assert_frame_not_equal

from pyfuppes import timecorr


def _make_df(dt_list):
    df = pl.DataFrame({"datetime": dt_list, "values": list(range(len(dt_list)))})
    return df.with_columns(
        pl.col("datetime").str.strptime(pl.Datetime, format="%Y-%m-%d").cast(pl.Datetime)
    )


class TestTimecorr(unittest.TestCase):
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

    def test_correct_time(self):
        # offset only
        order = 1
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([2, 3, 4, 5, 6, 7], dtype=np.float32)
        result = timecorr.correct_time(t, r, order)
        self.assertTrue(np.isclose(result.t_corr, r).all())

        t = np.array([-2, -1, 0, 1, 2, 3], dtype=np.float32)
        r = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        result = timecorr.correct_time(t, r, order)
        self.assertTrue(np.isclose(result.t_corr, r).all())

        # changed order
        order = 3
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([2, 3, 4, 5, 6, 7], dtype=np.float32)
        result = timecorr.correct_time(t, r, order)
        self.assertTrue(np.isclose(result.t_corr, r).all())

        # inclination only
        order = 1
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([1, 3, 5, 7, 9, 11], dtype=np.float32)
        result = timecorr.correct_time(t, r, order)
        self.assertTrue(np.isclose(result.t_corr, r).all())

        # inclination + offset
        order = 1
        t = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        r = np.array([2.0, 3.5, 5.0, 6.5, 8.0, 9.5], dtype=np.float32)
        result = timecorr.correct_time(t, r, order)
        self.assertTrue(np.isclose(result.t_corr, r).all())

    def test_pldt_filter(self):
        # edge case: first invalid
        have = ["2022-10-30", "2022-10-28", "2022-10-29"]
        # want_forward = ["2022-10-30"]
        # want_backward = ["2022-10-28", "2022-10-29"]

        df = _make_df(have)
        n, df_out = timecorr.filter_dt_forward(df)
        self.assertEqual(n, 2)
        self.assertTrue((df_out["values"] == pl.Series([0])).all())
        assert_frame_not_equal(df, df_out)

        df = _make_df(have)
        n, df_out = timecorr.filter_dt_backward(df)
        self.assertEqual(n, 1)
        self.assertTrue((df_out["values"] == pl.Series([1, 2])).all())
        assert_frame_not_equal(df, df_out)

        # edge case: last invalid
        have = ["2022-10-29", "2022-10-30", "2022-10-29"]
        # want_forward = ["2022-10-29", "2022-10-30"]

        df = _make_df(have)
        n, df = timecorr.filter_dt_forward(df)
        self.assertEqual(n, 1)
        self.assertTrue((df["values"] == pl.Series([0, 1])).all())

        # some invalid key
        have = ["2022-10-29", "2022-10-30", "2022-10-28", "2022-10-31"]
        # want_forward = ["2022-10-29", "2022-10-30", "2022-10-31"]
        # want_backward = ["2022-10-28", "2022-10-31"]

        df = _make_df(have)
        n, df = timecorr.filter_dt_forward(df)
        self.assertEqual(n, 1)
        self.assertTrue((df["values"] == pl.Series([0, 1, 3])).all())

        df = _make_df(have)
        n, df = timecorr.filter_dt_backward(df)
        self.assertEqual(n, 2)
        self.assertTrue((df["values"] == pl.Series([2, 3])).all())

        have = ["2022-10-29", "2022-10-30", "2022-11-01", "2022-10-31"]
        # want_forward = ["2022-10-29", "2022-10-30", "2022-11-01"]
        # want_backward = ["2022-10-29", "2022-10-30", "2022-10-31"]

        df = _make_df(have)
        n, df = timecorr.filter_dt_forward(df)
        self.assertEqual(n, 1)
        self.assertTrue((df["values"] == pl.Series([0, 1, 2])).all())

        df = _make_df(have)
        n, df = timecorr.filter_dt_backward(df)
        self.assertEqual(n, 1)
        self.assertTrue((df["values"] == pl.Series([0, 1, 3])).all())

        have = ["2022-10-29", "2022-10-30", "2022-10-28", "2022-10-30"]
        # want_forward = ["2022-10-29", "2022-10-30"]
        # want_backward = ["2022-10-28", "2022-10-30"]

        df = _make_df(have)
        n, df = timecorr.filter_dt_forward(df)
        self.assertEqual(n, 2)
        self.assertTrue((df["values"] == pl.Series([0, 1])).all())

        df = _make_df(have)
        n, df_out = timecorr.filter_dt_backward(df)
        self.assertEqual(n, 2)
        self.assertTrue((df_out["values"] == pl.Series([2, 3])).all())
        assert_frame_not_equal(df, df_out)

    def test_xcorr_timelag(self):
        # signal with peak
        t = np.linspace(0, 250, 250)
        f = 10 * np.exp(-((t - 90) ** 2) / 8) + np.random.randn(250) + 99
        g = 10 * np.exp(-((t - 180) ** 2) / 8) + np.random.randn(250) + 41
        lag = timecorr.xcorr_timelag(t, f, t, g, show_plots=False)
        # print(l, 90)
        self.assertTrue(abs(lag - 90) < (90 * 0.02))  # shift is 90... expect within 2%

        # Sawtooth wave
        # https://stackoverflow.com/questions/4688715/find-time-shift-between-two-similar-waveforms
        f = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0, 0, 0])
        g = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 1, 0])
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
        f, g = data[to_freq : 4 * to_freq], data[: 3 * to_freq]
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
        lag = timecorr.xcorr_timelag(x0, f, x0, g, xrange=(x0.min(), x1.max()), show_plots=False)  # type: ignore
        # print(l, shift*-1)
        # shift is 90... expect within 2%
        self.assertTrue(abs(lag - 3) < (3 * 0.02))


if __name__ == "__main__":
    unittest.main()
