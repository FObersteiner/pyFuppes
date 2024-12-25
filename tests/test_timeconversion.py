# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import xarray as xr

from pyfuppes import timeconversion


class TestTimeconv(unittest.TestCase):
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

    def test_xrtime_to_mdns(self):
        da = xr.DataArray(
            data=[1, 2, 3],
            dims=["Time"],
            coords={"Time": pd.date_range("2014-09-06", periods=3)},
        )
        t = timeconversion.xrtime_to_mdns(da)
        self.assertTrue(isinstance(t, np.ndarray))
        self.assertTrue(t.dtype.kind == "f")  # f --> floating point number
        self.assertTrue(issubclass(t.dtype.type, np.floating))
        self.assertListEqual([0.0, 86400.0, 172800.0], list(t))

    def test_dtstr_2_mdns(self):
        # no timezone
        t = ["2012-01-01T01:00:00", "2012-01-01T02:00:00"]
        f = "%Y-%m-%dT%H:%M:%S"
        result = list(map(int, timeconversion.dtstr_2_mdns(t, f)))
        self.assertEqual(result, [3600, 7200])
        # with timezone
        t = ["2012-01-01T01:00:00+02:00", "2012-01-01T02:00:00+02:00"]
        f = "%Y-%m-%dT%H:%M:%S%z"
        result = list(map(int, timeconversion.dtstr_2_mdns(t, f)))
        self.assertEqual(result, [3600, 7200])
        # varying UTC offset
        t = ["2012-01-01T01:00:00+02:00", "2012-01-01T02:00:00+01:00"]
        f = "%Y-%m-%dT%H:%M:%S%z"
        with self.assertRaises(AssertionError):
            _ = list(map(int, timeconversion.dtstr_2_mdns(t, f)))
        # zero case
        t = "2012-01-01T00:00:00+02:00"
        result = timeconversion.dtstr_2_mdns(t, f)
        self.assertEqual(int(result), 0)

    def test_dtobj_2_mdns(self):
        t = [datetime(2000, 1, 1, 1), datetime(2000, 1, 1, 2)]
        result = list(map(int, timeconversion.dtobj_2_mdns(t)))
        self.assertEqual(result, [3600, 7200])
        t = [
            datetime(2000, 1, 1, 1, tzinfo=timezone.utc),
            datetime(2000, 1, 1, 2, tzinfo=timezone.utc),
        ]
        result = list(map(int, timeconversion.dtobj_2_mdns(t)))
        self.assertEqual(result, [3600, 7200])

    def test_unixtime_2_mdns(self):
        t = [3600, 7200, 10800]
        result = list(map(int, timeconversion.unixtime_2_mdns(t)))
        self.assertEqual(result, t)

    def test_mdns_2_dtobj(self):
        t = [3600, 10800, 864000]
        ref = datetime(2020, 5, 15, tzinfo=timezone.utc)
        result = list(map(int, timeconversion.mdns_2_dtobj(t, ref, posix=True)))
        self.assertEqual(result, [1589504400, 1589511600, 1590364800])

    def test_daysSince_2_dtobj(self):
        t0, off = datetime(2020, 5, 10), 10.5
        result = timeconversion.daysSince_2_dtobj(t0, off)
        self.assertEqual(result.hour, 12)
        self.assertEqual(result.day, 20)

    def test_dtstr_2_unix(self):
        result = timeconversion.dtstr_2_unixtime("2020-05-15", "%Y-%m-%d")
        self.assertAlmostEqual(result, datetime(2020, 5, 15, tzinfo=timezone.utc).timestamp())


if __name__ == "__main__":
    unittest.main()
