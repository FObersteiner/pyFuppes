# -*- coding: utf-8 -*-
import unittest

import numpy as np
import pandas as pd
import polars as pl
from pandas import testing as pdtest
from polars.testing import assert_series_equal
from pyfuppes import interpolate


class TestInterpolate(unittest.TestCase):
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

    # --------------------------------------------------------------------------------

    def test_interp_df(self):
        # high to low freq:
        df_src = pd.DataFrame(
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
        df_src.index = pd.to_datetime(df_src["dt"]).astype("int64")
        new_index = (
            pd.to_datetime(
                [
                    "2022-12-14T14:00:01.500",
                    "2022-12-14T14:00:03.500",
                    "2022-12-14T14:00:05.500",
                ]
            )
            .to_series()
            .astype("int64")
        )
        new_index.name = df_src.index.name
        df_out = interpolate.pd_DataFrame_ip(df_src, new_index)
        self.assertIsNone(
            pdtest.assert_series_equal(
                df_out["v1_ip"], pd.Series([1.5, 3.5, 5.5], name="v1_ip", index=new_index)
            )
        )

        # low to high freq:
        df_src = pd.DataFrame(
            {
                "dt": [
                    "2022-12-14T14:00:01.500",
                    "2022-12-14T14:00:03.500",
                    "2022-12-14T14:00:05.500",
                ],
                "v1": [1.5, 3.5, 5.5],
            }
        )
        df_src.index = pd.to_datetime(df_src["dt"]).astype("int64")
        new_index = (
            pd.to_datetime(
                [
                    "2022-12-14T14:00:01.000",
                    "2022-12-14T14:00:02.000",
                    "2022-12-14T14:00:03.000",
                    "2022-12-14T14:00:04.000",
                    "2022-12-14T14:00:05.000",
                    "2022-12-14T14:00:06.000",
                ]
            )
            .to_series()
            .astype("int64")
        )
        new_index.name = df_src.index.name
        df_out = interpolate.pd_DataFrame_ip(df_src, new_index)
        self.assertIsNone(
            pdtest.assert_series_equal(
                df_out["v1_ip"],
                # edge values are only repeated, does not extrapolate:
                pd.Series([1.5, 2.0, 3.0, 4.0, 5.0, 5.5], name="v1_ip", index=new_index),
            )
        )

    # --------------------------------------------------------------------------------

    def test_pd_Series_interp1d(self):
        # low to high freq:
        df_dst = pd.DataFrame(
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
        df_dst["dt"] = pd.to_datetime(df_dst["dt"]).astype("int64")
        df_src = pd.DataFrame(
            {
                "dt": [
                    "2022-12-14T14:00:01.500",
                    "2022-12-14T14:00:03.500",
                    "2022-12-14T14:00:05.500",
                ],
                "v1": [1.5, 3.5, 5.5],
            }
        )
        df_src["dt"] = pd.to_datetime(df_src["dt"]).astype("int64")
        df_out = interpolate.pd_Series_ip1d(
            df_src,
            df_dst,
            ivar_src_name="dt",
            dvar_src_name="v1",
            ivar_dst_name="dt",
            dvar_dst_name="v1_ip",
            kind="linear",  # no effect with pl_Series_ip1d_lite
            bounds_error=False,  # no effect with pl_Series_ip1d_lite
            fill_value="extrapolate",
        )
        with self.assertRaises(AssertionError):
            pdtest.assert_frame_equal(df_dst, df_out)

        self.assertIsNone(
            pdtest.assert_series_equal(
                df_out["v1_ip"], pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], name="v1_ip")
            )
        )

        df_out = interpolate.pd_Series_ip1d(
            df_src,
            df_dst,
            ivar_src_name="dt",
            dvar_src_name="v1",
            ivar_dst_name="dt",
            dvar_dst_name="v1_ip",
            kind="linear",  # no effect with pl_Series_ip1d_lite
            bounds_error=False,  # no effect with pl_Series_ip1d_lite
            fill_value=np.nan,
        )
        self.assertIsNone(
            pdtest.assert_series_equal(
                df_out["v1_ip"],
                pd.Series([np.nan, 2.0, 3.0, 4.0, 5.0, np.nan], name="v1_ip"),
            )
        )
        # high to low freq:
        df_src = pd.DataFrame(
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
        df_src["dt"] = pd.to_datetime(df_src["dt"]).astype("int64")
        df_dst = pd.DataFrame(
            {
                "dt": [
                    "2022-12-14T14:00:01.500",
                    "2022-12-14T14:00:03.500",
                    "2022-12-14T14:00:05.500",
                ],
            }
        )
        df_dst["dt"] = pd.to_datetime(df_dst["dt"]).astype("int64")
        df_out = interpolate.pd_Series_ip1d(
            df_src,
            df_dst,
            ivar_src_name="dt",
            ivar_dst_name="dt",
            dvar_src_name="v1",
            dvar_dst_name="v1_ip",
            kind="linear",  # no effect with pl_Series_ip1d_lite
            bounds_error=True,  # no effect with pl_Series_ip1d_lite
        )
        with self.assertRaises(AssertionError):
            pdtest.assert_frame_equal(df_dst, df_out)
        self.assertIsNone(
            pdtest.assert_series_equal(df_out["v1_ip"], pd.Series([1.5, 3.5, 5.5], name="v1_ip"))
        )

    # --------------------------------------------------------------------------------

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
            df_dst = df_dst.with_columns(pl.col("dt").str.strptime(pl.Datetime))
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
            df_src = df_src.with_columns(pl.col("dt").str.strptime(pl.Datetime))
            df_dst = func(
                df_src,
                df_dst,
                ivar_src_name="dt",
                ivar_dst_name="dt",
                dvar_src_name="v1",
                dvar_dst_name="v1_ip",
                kind="linear",  # no effect with pl_Series_ip1d_lite
                bounds_error=False,  # no effect with pl_Series_ip1d_lite
                fill_value="extrapolate",
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
                fill_value=np.nan,
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
            df_src = df_src.with_columns(pl.col("dt").str.strptime(pl.Datetime))
            df_dst = pl.DataFrame(
                {
                    "dt": [
                        "2022-12-14T14:00:01.500",
                        "2022-12-14T14:00:03.500",
                        "2022-12-14T14:00:05.500",
                    ],
                }
            )
            df_dst = df_dst.with_columns(pl.col("dt").str.strptime(pl.Datetime))
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
                assert_series_equal(df_dst["v1_ip"], pl.Series("v1_ip", [1.5, 3.5, 5.5]))
            )


if __name__ == "__main__":
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        unittest.main()
