import unittest

from datetime import datetime, timezone

from pyfuppes import timeconversion


class TestTimeconv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # to run before all tests
        print("testing pyfuppes.timeconversion...")

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

    def test_posix_2_mdns(self):
        t = [3600, 7200, 10800]
        result = list(map(int, timeconversion.posix_2_mdns(t)))
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

    def test_dtstr_2_posix(self):
        result = timeconversion.dtstr_2_posix("2020-05-15", "%Y-%m-%d")
        self.assertAlmostEqual(
            result, datetime(2020, 5, 15, tzinfo=timezone.utc).timestamp()
        )


if __name__ == "__main__":
    unittest.main()
