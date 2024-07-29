# -*- coding: utf-8 -*-
"""Geospatial helpers, such as Haversine distance or solar zenith angle."""

from datetime import datetime
from math import acos, asin, cos, degrees, floor, radians, sin, sqrt

import numpy as np
from geopy import distance
from numba import njit
from pysolar.solar import get_altitude


# trigonometry with degrees:
def _cos2(x):
    return cos(radians(x))


def _sin2(x):
    return sin(radians(x))


def _acos2(x):
    return degrees(acos(x))


###############################################################################

EARTH_RADIUS = 6372.8  # approximate radius of earth in km


@njit
def haversine_dist(lat: np.ndarray, lon: np.ndarray) -> float:
    """Calculate Haversine distance in km along lat/lon coordinates. Code gets numba-JIT compiled."""
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    dist = 0

    lat1, lon1 = lat[0], lon[0]
    for j in range(1, lat.shape[0]):
        lat0, lat1 = lat1, lat[j]
        lon0, lon1 = lon1, lon[j]

        dLat = radians(lat1 - lat0)
        dLon = radians(lon1 - lon0)
        lat0 = radians(lat0)
        lat1 = radians(lat1)

        a = sin(dLat / 2) ** 2 + cos(lat0) * cos(lat1) * sin(dLon / 2) ** 2
        c = 2 * asin(sqrt(a))

        dist += EARTH_RADIUS * c

    return dist


###############################################################################


def geodesic_dist(lat: np.ndarray, lon: np.ndarray) -> float:
    """Calculate geodesic distance in km along lat/lon coordinates using geopy module."""
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    dist = 0.0
    for j in range(lat.shape[0] - 1):
        dist += distance.geodesic((lat[j], lon[j]), (lat[j + 1], lon[j + 1]), ellipsoid="WGS-84").km

    return dist


###############################################################################


def sza_pysolar(
    UTC: datetime,
    latitude: float,
    longitude: float,
) -> float:
    """Compute solar zenith angle with get_altitude function from pysolar package."""
    return 90 - get_altitude(latitude, longitude, UTC)


# another option to calculate SZA would be to use astropy; for instance like
#
# from astropy.coordinates import get_sun, AltAz, EarthLocation
# from astropy.time import Time
#
# lon, lat = 42, 55
# sun_time = Time('2017-12-6 17:00') # UTC
# loc = EarthLocation.from_geodetic(lon, lat)
# altaz = AltAz(obstime=sun_time, location=loc)
# zen_ang = get_sun(sun_time).transform_to(altaz).zen
#
# see e.g. https://stackoverflow.com/a/47678091/10197418


def sza(
    UTC: datetime,
    latitude: float,
    longitude: float,
) -> float:
    """
    Calculate the solar zenith angle (in degree).

    UTC         (as datetime.datetime Object)
    longitude   (in degree)
    latitude    (in degree)

    Code adapted from https://www.python-forum.de/viewtopic.php?t=21117
    (2018-10-17 8:10 UTC)
    """

    day_of_year = UTC.timetuple().tm_yday
    leap_year_factor = (-0.375, 0.375, -0.125, 0.125)[UTC.year % 4]
    UTC_min = UTC.hour * 60.0 + UTC.minute + UTC.second / 60.0
    J = 360.0 / 365.0 * (day_of_year + leap_year_factor + UTC_min / 1440.0)

    # hour angle (using the time equation)
    average_localtime = UTC_min + 4 * longitude
    true_solar_time = (
        average_localtime
        + 0.0066
        + 7.3525 * _cos2(J + 85.9)
        + 9.9359 * _cos2(2 * J + 108.9)
        + 0.3387 * _cos2(3 * J + 105.2)
    )
    hour_angle = 15.0 * (720.0 - true_solar_time) / 60.0

    # sun declination, using DIN 5034-2
    declination = (
        0.3948
        - 23.2559 * _cos2(J + 9.1)
        - 0.3915 * _cos2(2 * J + 5.4)
        - 0.1764 * _cos2(3 * J + 26.0)
    )

    # solar zenith angle
    return _acos2(
        _sin2(latitude) * _sin2(declination)
        + _cos2(hour_angle) * _cos2(latitude) * _cos2(declination)
    )


###############################################################################


def get_EoT(date_ts: datetime) -> float:
    """
    Calculate equation of time, for calculation of local solar time.

    input: date_ts - datetime object

    returns: equation of time result - float
    """
    B = (360 / 365) * (date_ts.timetuple().tm_yday - 81)

    return 9.87 * sin(2 * B) - 7.53 * cos(B) - 1.5 * sin(B)


###############################################################################


def get_LSTdayFrac(
    longitude: float, tz_offset: float, EoT: float, days_delta: float, time_delta: float
) -> float:
    """
    Calculate local solar time as a fraction of a day.

    input:
        longitude: -180 to +180 degrees west to east, float
        tz_offset: time zone offset from UTC in hours, float
        EoT: equation of time for selected date, float
        days_delta: days since reference date, float
        time_delta: current time as days since reference date, float
    returns:
        local solar time as day fraction (float, 0-1)
    """
    LSTM = 15 * tz_offset  # Local Standard Time Meridian
    t_corr = (4 * (longitude - LSTM) + EoT) / 60 / 24  # [d]
    LST_frac = (time_delta + tz_offset / 24 - days_delta) + t_corr
    if LST_frac > 1:
        return LST_frac - floor(LST_frac)
    return LST_frac
