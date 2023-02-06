# -*- coding: utf-8 -*-

import unittest
from io import StringIO, BytesIO
from pathlib import Path

import polars as pl

from pyfuppes.na1001 import FFI1001 as na1001

try:
    wd = Path(__file__).parent
except NameError:
    wd = Path.cwd()
assert wd.is_dir(), "faild to obtain working directory"

src, dst = wd / "test_input", wd / "test_output"


class TestNa1001(unittest.TestCase):
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

    def test_read_valid(self):
        file = src / "validate_na/valid_1001a.na"
        na = na1001(file, sep_data=" ", rmv_repeated_seps=True)
        self.assertIsNotNone(na)
        s = na.__repr__()
        self.assertTrue(len(s) > 10)
        self.assertEqual(na.NV, 2)
        self.assertEqual(na.NLHEAD, 36)
        self.assertEqual(len(na.HEADER), na.NLHEAD)

        file = src / "validate_na/OM_20200304_591_CPT_MUC_V01_valid0.txt"
        na = na1001(file, sep_data="\t")
        self.assertEqual(len(na.HEADER), na.NLHEAD)

    def test_invalid_read_config(self):
        file = src / "validate_na/valid_1001a.na"
        with self.assertRaises(Exception):
            na1001(file, rmv_repeated_seps=False)

    def test_validate(self):
        # cases
        # (filepath, expect_fail?)
        cases = sorted(
            (f, "invalid" in f.name) for f in (src / "validate_na").glob("*.txt")
        )
        self.assertNotEqual([], cases)
        for path, expect_fail in cases:
            if expect_fail:
                with self.assertRaises(Exception):
                    _ = na1001(path)
            else:
                result = na1001(path)
                self.assertIsNotNone(result)

    def test_read_from_io(self):
        s = """37 1001
F. Obersteiner; A. Zahn; f.obersteiner@kit.edu; andreas.zahn@kit.edu
Institute for Meteorology and Climate Research (IMK), Karlsruhe Institute of Technology (KIT), 76021 Karlsruhe, P.O. Box 3640, Germany
Ozone measured with the dual-beam UV-photometer that is part of the FAIRO instrument during IAGOS-CARIBIC (onboard A340-600 D-AIHE of Lufthansa)
IAGOS-CARIBIC (CARIBIC-2), http://www.caribic-atmospheric.com/
1 1
2020 03 04 2020 09 22
0
TimeCRef; CARIBIC_reference_time_since_0_hours_UTC_on_first_date_in_line_7; [s]
1
1
9999
Ozone; Ozone volume mixing ratio; [ppb]
8
FileFormatVersionInfo: CARIBIC_NAmes_v02 standard # This file was created according to the conventions for CARIBIC NASA Ames data files, given by 'Info_Nasa_Ames_Format_02.zip'.
FlightNo: 591
FlightRoute: CPT MUC # IATA code of DepartureAirport and ArrivalAirport
DepartureAirport: Cape Town
ArrivalAirport: Munich
FileName: OM_20200304_591_CPT_MUC_V01.txt
ExceptionToConsider: no
ChangeLog: 0
14
FAIRO eval software version: 2019.11.21a
Info on adjustments of the independent variable:
Measurement time-stamp is synchronized to CARIBIC master PC time.
Info on measurement uncertainty:
Uncertainty is estimated to be at least 1 ppb OR 2.0% for the UV photometer and 2.5% combined for the chemiluminescence detector (use whatever value is larger).
#
The following two lines contain standard names and units according to the 'NetCDF Climate and Forecast (CF) Metadata Convention', see http://cfconventions.org/. Each entry (name or unit) corresponds to a certain column; the entry before the first tab belongs to the independent column.
CF_StandardNames: time	mole_fraction_of_ozone_in_air
CF_Units: [s]	[1e-9]
The following four lines contain: Start date like in line 7 (formatted as YYYYMMDD), followed by the multiplicators like in line 11; Line number containing the KeyLabel 'ExceptionToConsider' (0 if no such exception is mentioned), followed by the NaN-values like in line 12; Units like in lines 13ff; Column headers.
20200304	1
0	9999
[s]	[ppb]
TimeCRef	Ozone"""
        with self.assertRaises(AssertionError):
            _ = na1001(StringIO(s))  # header-only not allowed by default

        na = na1001(StringIO(s), allow_emtpy_data=True)
        self.assertEqual(len(na.HEADER), na.NLHEAD)

        na = na1001(BytesIO(bytes(s, "utf-8")), allow_emtpy_data=True)
        self.assertEqual(len(na.HEADER), na.NLHEAD)

    def test_poldf(self):
        file = src / "validate_na/OM_20200304_591_CPT_MUC_V01_valid0.txt"
        na = na1001(file, sep_data="\t")
        df = na.to_poldf(add_datetime=True)
        self.assertTrue(isinstance(df, pl.DataFrame))
        self.assertTrue("datetime" in df.columns)


if __name__ == "__main__":
    unittest.main()
