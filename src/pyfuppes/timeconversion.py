# -*- coding: utf-8 -*-
"""
Created on Fri May 15 11:35:38 2020

@author: F. Obersteiner, f/obersteiner//kit/edu
"""

from datetime import datetime, timedelta, timezone
import numpy as np


### HELPERS ###################################################################


def to_list(parm, is_scalar=False):
    """
    convert input "parm" to a Python list object.
    if "parm" is a scalar, return value "is_scalar" is True, otherwise False.
    """
    if isinstance(parm, str): # check this first: don't call list() on a string
        parm, is_scalar = [parm], True
    elif not isinstance(parm, (list, np.ndarray)):
        try:
            parm = list(parm) # call list() first in case parm is np.ndarray
        except TypeError: # will e.g. raised if parm is a float
            parm = [parm]
        is_scalar = True
    return parm, is_scalar


### MAIN FUNCTIONS ############################################################


def dtstr_2_mdns(timestring,
                 tsfmt: str = "%Y-%m-%d %H:%M:%S.%f",
                 ymd: tuple = None):
    """
    convert datetime string to seconds since midnight (float).
    since a relative difference is calculated, the function is timezone-safe.

    Parameters
    ----------
    timestring : str, list of str or np.ndarray with dtype str/obj.
        timestamp given as string.
    tsfmt : str, optional
        timestring format. The default is "%Y-%m-%d %H:%M:%S.%f".
    ymd : tuple, optional
        starting date as tuple of integers; (year, month, day).
        The default is None.

    Returns
    -------
    float; scalar or float; list
        seconds since midnight for the given timestring(s).

    """
    timestring, ret_scalar = to_list(timestring)
    if tsfmt == 'iso':
        dt = [datetime.fromisoformat(s) for s in timestring]
    else:
        dt = [datetime.strptime(s, tsfmt) for s in timestring]

    if ymd:  # [yyyy,m,d] given, take that as starting point
        t0 = (datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                       hour=0, minute=0, second=0, microsecond=0,
                       tzinfo=dt[0].tzinfo))
    else:  # use date from timestring as starting point
        t0 = dt[0].replace(hour=0, minute=0, second=0, microsecond=0)

    mdns = [(s - t0).total_seconds() for s in dt]

    return mdns[0] if ret_scalar else mdns


###############################################################################


def dtobj_2_mdns(dt_obj,
                 ref_is_first: bool = False,
                 ref_date: tuple = False):
    """
    convert a Python datetime object (or list/array of ...) to seconds
    after midnight.

    Parameters
    ----------
    dt_obj : datetime object or list/array of datetime objects
        the datetime to be converted to seconds after midnight.
    ref_is_first : bool, optional
        first entry of dt_obj list/array defines start date.
        The default is False.
    ref_date : tuple of int, optional
        custom start date given as (year, month, day). The default is False.

    Returns
    -------
    float; scalar or list of float
        seconds after midnight for the given datetime object(s).

    """
    dt_obj, ret_scalar = to_list(dt_obj)

    tzs = [d.tzinfo for d in dt_obj]
    assert len(set(tzs)) == 1, "all timezones must be equal."

    if ref_date:
        t0 = datetime(*ref_date, tzinfo=dt_obj[0].tzinfo)
    elif ref_is_first:
        t0 = dt_obj[0]

    if ref_is_first or ref_date:
        result = ([(x-t0.replace(hour=0, minute=0, second=0, microsecond=0))
                   .total_seconds() for x in dt_obj])
    else:
        result = ([(x-x.replace(hour=0, minute=0, second=0, microsecond=0))
                   .total_seconds() for x in dt_obj])

    return result[0] if ret_scalar else result


###############################################################################


def posix_2_mdns(posixts,
                 ymd: tuple = None):
    """
    convert a POSIX timestamp (or list/array of ...) to seconds after midnight.

    Parameters
    ----------
    posixts : float, list of float or np.ndarray with dtype float.
        the POSIX timestamp to be converted to seconds after midnight.
    ymd : tuple of int, optional
        define starting date as tuple of integers (year, month, day) UTC.
        The default is None, which means the reference date is the day of the
        timestamp.

    Returns
    -------
    float; scalar or list of float
        seconds after midnight for the given POSIX timestamp(s).

    """
    posixts, ret_scalar = to_list(posixts)

    if ymd:  # (yyyy, m, d) given, take that as starting point t0:
        t0 = datetime(year=ymd[0], month=ymd[1], day=ymd[2],
                      tzinfo=timezone.utc).timestamp()
    else: # take date of first entry as starting point
        t0 = datetime.fromtimestamp(posixts[0], tz=timezone.utc)
        t0 = t0.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    ts = [t-t0 for t in posixts]

    return ts[0] if ret_scalar else ts


###############################################################################


def mdns_2_dtobj(mdns,
                 ref_date,
                 assume_UTC: bool = True,
                 posix: bool = False,
                 str_fmt: str = False):
    """
    convert seconds after midnight (or list/array of ...) to datetime object.

    Parameters
    ----------
    mdns : float, list of float or np.ndarray with dtype float.
        the seconds after midnight to be converted to datetime object(s).
    ref_date : tuple of int (year, month, day) or datetime object
        date that mdns refers to.
    assume_UTC : boolean.
        if ref_date is supplied as a y/m/d tuple, add tzinfo UTC.
    posix : bool, optional
        return POSIX timestamp(s). The default is False.
    str_fmt : str, optional
        Format for datetime.strftime, e.g. "%Y-%m-%d %H:%M:%S.%f"
        If provided, output is delivered as formatted string. POSIX must
            be False in that case, or STR_FMT is overridden (evaluated last).
        The default is False.

    Returns
    -------
    datetime object or float (POSIX timestamp)
        ...for the given seconds after midnight.

    """
    mdns, ret_scalar = to_list(mdns)
    # ensure type float:
    if not isinstance(mdns[0], (float, np.float32, np.float64)):
        mdns = list(map(float, mdns))

    # check if ref_date is supplied as a y/m/d tuple. convert to datetime.
    reset_tz = False
    if isinstance(ref_date, (tuple, list)):
        ref_date, reset_tz = datetime(*ref_date), True
        if assume_UTC: # add timezone UTC if assume_UTC is set to True
            ref_date = ref_date.replace(tzinfo=timezone.utc)

    result = [ref_date + timedelta(seconds=t) for t in mdns]

    if posix:
        if not ref_date.tzinfo:
            print("*mdns_2_dtobj warning*: creating POSIX timestamps from "
                  "naive datetime objects might give unexpected results!\n"
                  "\t-> consider passing a tz-aware ref_date instead.")
        result = [dtobj.timestamp() for dtobj in result]
    elif str_fmt:
        offset = -3 if str_fmt.endswith("%f") else None
        result = [dtobj.strftime(str_fmt)[:offset] for dtobj in result]

    if reset_tz:
        result = [t.replace(tzinfo=None) for t in result]

    return result[0] if ret_scalar else result


###############################################################################


def daysSince_2_dtobj(day0, daysSince):
    """
    Convert a floating point number "daysSince" to a datetime object.
    day0: datetime object, from when to count.

    Parameters
    ----------
    day0 : datetime object (naive or tz-aware)
        from when to count.
    daysSince : int or float
        number of days.

    Returns
    -------
    datetime object

    """
    if isinstance(daysSince, (list, np.ndarray)):
        return [(day0 + timedelta(days=ds)) for ds in daysSince]
    return (day0 + timedelta(days=daysSince))


###############################################################################


def dtstr_2_posix(timestring,
                  tsfmt: str = "%Y-%m-%d %H:%M:%S.%f",
                  tz=timezone.utc):
    """
    Convert timestring without timezone information to UTC timestamp.

    Parameters
    ----------
    timestring : string
        representing date (and time).
    tsfmt : str, optional
        strptime format. The default is "%Y-%m-%d %H:%M:%S.%f".
    tz : timezone, optional
        The default is timezone.utc.

    Returns
    -------
    POSIX timestamp
        UTC seconds since the epoch 1970-01-01.

    """
    if tsfmt == 'iso':
        return datetime.fromisoformat(timestring).replace(tzinfo=tz).timestamp()
    return datetime.strptime(timestring, tsfmt).replace(tzinfo=tz).timestamp()


###############################################################################
