# -*- coding: utf-8 -*-
import unittest

import numpy as np
import polars as pl
from polars.testing import assert_series_equal

from pyfuppes import interpolate


class TestCfg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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

    def test_pl_Series_interp1d(self):
        for func in interpolate.pl_Series_interp1d, interpolate.pl_Series_ip1d_lite:
            # low to high freq:
            df_dst = pl.DataFrame(
                {
                    "dt": [
                        "2022-12-14T14:00:01.000",
                        "2022-12-14T14:00:02.000",
                        "2022-12-14T14:00:03.000",
                        "2022-12-14T14:00:04.000",
                        "2022-12-14T14:00:05.000",
                        "2022-12-14T14:00:06.000",
                    ]
                }
            )
            df_dst = df_dst.with_column(pl.col("dt").str.strptime(pl.Datetime))
            df_src = pl.DataFrame(
                {
                    "dt": [
                        "2022-12-14T14:00:01.500",
                        "2022-12-14T14:00:03.500",
                        "2022-12-14T14:00:05.500",
                    ],
                    "v1": [1.5, 3.5, 5.5],
                }
            )
            df_src = df_src.with_column(pl.col("dt").str.strptime(pl.Datetime))
            df_dst = func(
                df_src,
                df_dst,
                ivar_src_name="dt",
                ivar_dst_name="dt",
                dvar_src_name="v1",
                dvar_dst_name="v1_ip",
                kind="linear",  # no effect with pl_Series_ip1d_lite
                bounds_error=False,  # no effect with pl_Series_ip1d_lite
                fill_value="extrapolate",  # no effect with pl_Series_ip1d_lite
            )
            self.assertIsNone(
                assert_series_equal(
                    df_dst["v1_ip"], pl.Series("v1_ip", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
                )
            )
            df_dst = func(
                df_src,
                df_dst,
                ivar_src_name="dt",
                ivar_dst_name="dt",
                dvar_src_name="v1",
                dvar_dst_name="v1_ip",
                kind="linear",  # no effect with pl_Series_ip1d_lite
                bounds_error=False,  # no effect with pl_Series_ip1d_lite
                fill_value=np.nan,  # no effect with pl_Series_ip1d_lite
            )
            self.assertIsNone(
                assert_series_equal(
                    df_dst["v1_ip"],
                    pl.Series("v1_ip", [np.nan, 2.0, 3.0, 4.0, 5.0, np.nan]),
                )
            )
            # high to low freq:
            df_src = pl.DataFrame(
                {
                    "dt": [
                        "2022-12-14T14:00:01.000",
                        "2022-12-14T14:00:02.000",
                        "2022-12-14T14:00:03.000",
                        "2022-12-14T14:00:04.000",
                        "2022-12-14T14:00:05.000",
                        "2022-12-14T14:00:06.000",
                    ],
                    "v1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                }
            )
            df_src = df_src.with_column(pl.col("dt").str.strptime(pl.Datetime))
            df_dst = pl.DataFrame(
                {
                    "dt": [
                        "2022-12-14T14:00:01.500",
                        "2022-12-14T14:00:03.500",
                        "2022-12-14T14:00:05.500",
                    ],
                }
            )
            df_dst = df_dst.with_column(pl.col("dt").str.strptime(pl.Datetime))
            df_dst = func(
                df_src,
                df_dst,
                ivar_src_name="dt",
                ivar_dst_name="dt",
                dvar_src_name="v1",
                dvar_dst_name="v1_ip",
                kind="linear",  # no effect with pl_Series_ip1d_lite
                bounds_error=True,  # no effect with pl_Series_ip1d_lite
            )
            self.assertIsNone(
                assert_series_equal(
                    df_dst["v1_ip"], pl.Series("v1_ip", [1.5, 3.5, 5.5])
                )
            )


if __name__ == "__main__":
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        unittest.main()
