# -*- coding: utf-8 -*-
"""Geospatial helpers, such as Haversine distance or solar zenith angle."""

from datetime import datetime
from math import cos, sin, acos, atan2, radians, sqrt, degrees, floor

from geopy import distance
from numba import njit
from pysolar.solar import get_altitude

###############################################################################


@njit
def haversine_dist(lat, lon):
    """Calculate Haversine distance along lat/lon coordinates in km. Code gets numba-JIT compiled."""
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    R = 6371  # approximate radius of earth in km
    dist = 0

    lat1 = radians(lat[0])
    lon1 = radians(lon[0])
    for j in range(1, lat.shape[0]):
        lat0, lat1 = lat1, radians(lat[j])
        lon0, lon1 = lon1, radians(lon[j])

        dlon = lon1 - lon0
        dlat = lat1 - lat0

        a = sin(dlat / 2) ** 2 + cos(lat0) * cos(lat1) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        dist += R * c

    return dist


###############################################################################


def geodesic_dist(lat, lon):
    """Calculate geodesic distance along lat/lon coordinates using geopy module."""
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    dist = 0.0
    for j in range(lat.shape[0] - 1):
        dist += distance.geodesic(
            (lat[j], lon[j]), (lat[j + 1], lon[j + 1]), ellipsoid="WGS-84"
        ).km
    return dist


###############################################################################


def sza_pysolar(UTC=datetime.utcnow(), latitude=52.37, longitude=9.72):
    """Compute solar zenith angle with get_altitude function from pysolar package."""
    return 90 - get_altitude(latitude, longitude, UTC)


###############################################################################


def sza(UTC=datetime.utcnow(), latitude=52.37, longitude=9.72):
    """
    Calculate the solar zenith angle (in degree).

    UTC         (as datetime.datetime Object)
    longitude   (in degree)
    latitude    (in degree)

    Default values: Hannover, Germany

    Code adapted from https://www.python-forum.de/viewtopic.php?t=21117
    (2018-10-17 8:10 UTC)
    """

    # define trigonometry with degrees
    def cos2(x):
        return cos(radians(x))

    def sin2(x):
        return sin(radians(x))

    def acos2(x):
        return degrees(acos(x))

    # parameter
    day_of_year = UTC.timetuple().tm_yday
    leap_year_factor = (-0.375, 0.375, -0.125, 0.125)[UTC.year % 4]
    UTC_min = UTC.hour * 60.0 + UTC.minute + UTC.second / 60.0
    J = 360.0 / 365.0 * (day_of_year + leap_year_factor + UTC_min / 1440.0)

    # hour angle (using the time equation)
    average_localtime = UTC_min + 4 * longitude
    true_solar_time = (
        average_localtime
        + 0.0066
        + 7.3525 * cos2(J + 85.9)
        + 9.9359 * cos2(2 * J + 108.9)
        + 0.3387 * cos2(3 * J + 105.2)
    )

    hour_angle = 15.0 * (720.0 - true_solar_time) / 60.0

    # sun declination (using DIN 5034-2)
    declination = (
        0.3948
        - 23.2559 * cos2(J + 9.1)
        - 0.3915 * cos2(2 * J + 5.4)
        - 0.1764 * cos2(3 * J + 26.0)
    )

    # solar zenith angle
    return acos2(
        sin2(latitude) * sin2(declination)
        + cos2(hour_angle) * cos2(latitude) * cos2(declination)
    )


###############################################################################


def get_EoT(date_ts):
    """
    Calculate equation of time.

    input: date_ts, datetime object
    returns: equation of time (float)
    use for: calculation of local solar time
    """
    B = (360 / 365) * (date_ts.timetuple().tm_yday - 81)
    return 9.87 * sin(2 * B) - 7.53 * cos(B) - 1.5 * sin(B)


###############################################################################


def get_LSTdayFrac(longitude, tz_offset, EoT, days_delta, time_delta):
    """
    Calculate local solar time as a fraction of a day.

    input:
        longitude: -180 to +180 degrees west to east, float
        tz_offset: time zone offset to UTC in hours, float
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
        LST_frac -= floor(LST_frac)
    return LST_frac
