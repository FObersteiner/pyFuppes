# -*- coding: utf-8 -*-
"""
Created on Fri May 22 13:21:48 2020

@author: F. Obersteiner, f/obersteiner//kit/edu
"""

import math
from datetime import datetime

from numba import njit
from geopy import distance
from pysolar.solar import get_altitude


###############################################################################


@njit
def haversine_dist(lat, lon):
    """
    calculate Haversine distance along lat/lon coordinates.
    """
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    R = 6373 # approximate radius of earth in km
    dist = 0

    lat1 = math.radians(lat[0])
    lon1 = math.radians(lon[0])
    for j in range(1, lat.shape[0]):
        lat0, lat1 = lat1, math.radians(lat[j])
        lon0, lon1 = lon1, math.radians(lon[j])

        dlon = lon1 - lon0
        dlat = lat1 - lat0

        a = (math.sin(dlat/2)**2 +
             math.cos(lat0) * math.cos(lat1) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        dist += R * c

    return dist


###############################################################################


def geodesic_dist(lat, lon):
    """
    calculate geodesic distance along lat/lon coordinates using geopy module.
    """
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."
    dist = 0.
    for j in range(lat.shape[0]-1):
        dist += distance.geodesic((lat[j], lon[j]), (lat[j+1], lon[j+1]),
                                  ellipsoid='WGS-84').km
    return dist


###############################################################################


def sza_pysolar(UTC=datetime.utcnow(), latitude=52.37, longitude=9.72):
    """
    compute solar zenith angel
    uses get_altitude function from pysolar package
    """
    return 90 - get_altitude(latitude, longitude, UTC)


###############################################################################


def sza(UTC=datetime.utcnow(), latitude=52.37, longitude=9.72):
    '''
    Returns the solar zenith angle (in degree)

    UTC         (as datetime.datetime Object)
    longitude   (in degree)
    latitude    (in degree)

    Default values: Hannover, Germany

    Code adapted from https://www.python-forum.de/viewtopic.php?t=21117
    (2018-10-17 8:10 UTC)
    '''
    # define trigonometry with degrees
    cos2 = lambda x: math.cos(math.radians(x))
    sin2 = lambda x: math.sin(math.radians(x))
    acos2 = lambda x: math.degrees(math.acos(x))

    # parameter
    day_of_year = UTC.timetuple().tm_yday
    leap_year_factor = (-0.375, 0.375, -0.125, 0.125)[UTC.year % 4]
    UTC_min = UTC.hour * 60. + UTC.minute + UTC.second / 60.
    J = 360. / 365. * (day_of_year + leap_year_factor + UTC_min / 1440.)

    # hour angle (using the time equation)
    average_localtime = UTC_min + 4 * longitude
    true_solar_time = (average_localtime + 0.0066 + 7.3525 * cos2(  J +  85.9)
                                                  + 9.9359 * cos2(2*J + 108.9)
                                                  + 0.3387 * cos2(3*J + 105.2))

    hour_angle = 15. * (720. - true_solar_time) / 60.

    # sun declination (using DIN 5034-2)
    declination = (0.3948 - 23.2559 * cos2(  J + 9.1 )
                          -  0.3915 * cos2(2*J + 5.4 )
                          -  0.1764 * cos2(3*J + 26.))

    # solar zenith angle
    return acos2(sin2(latitude) * sin2(declination) +
                 cos2(hour_angle) * cos2(latitude) * cos2(declination))


###############################################################################


def get_EoT(date_ts):
    """
    input: date_ts, datetime object
    returns: equation of time (float)
    use for: calculation of local solar time
    """
    B = (360/365)*(date_ts.timetuple().tm_yday-81)
    return 9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)


###############################################################################


def get_LSTdayFrac(longitude, tz_offset, EoT, days_delta, time_delta):
    """
    input:
        longitude: -180 to +180 degrees west to east, float
        tz_offset: time zone offset to UTC in hours, float
        EoT: equation of time for selected date, float
        days_delta: days since reference date, float
        time_delta: current time as days since reference date, float
    returns:
        local solar time as day fraction (float, 0-1)
    """
    LSTM = 15 * tz_offset # Local Standard Time Meridian
    t_corr = (4 * (longitude - LSTM) + EoT)/60/24 # [d]
    LST_frac = (time_delta + tz_offset/24 - days_delta) + t_corr
    if LST_frac > 1:
        LST_frac -= math.floor(LST_frac)
    return LST_frac


