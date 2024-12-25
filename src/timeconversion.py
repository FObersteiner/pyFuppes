# -*- coding: utf-8 -*-
"""Convert between types representing date/time."""

import warnings
from datetime import datetime, timedelta, timezone
from operator import attrgetter
from typing import Any, Optional, Union

import numpy as np
import numpy.typing as npt
import xarray as xr

### HELPERS ###################################################################


def _to_list(
    parm: Union[Any, list[Any], np.ndarray], is_scalar: bool = False
) -> tuple[Union[list, np.ndarray], bool]:
    """
    Convert input "parm" to a Python list object.

    If "parm" is a scalar, return value "is_scalar" is True, otherwise False.
    """
    if isinstance(parm, str):  # check this first: don't call list() on a string
        parm, is_scalar = [parm], True
    elif not isinstance(parm, (list, np.ndarray)):
        try:
            parm = list(parm)  # call list() first in case parm is np.ndarray
        except TypeError:  # will e.g. raised if parm is a float
            parm = [parm]
        is_scalar = True

    return parm, is_scalar


### MAIN FUNCTIONS ############################################################


def xrtime_to_mdns(xrda: xr.DataArray, dim_name="Time") -> npt.NDArray[np.float64]:
    """
    Convert the time vector of an xarray.DataArray to an array representing seconds after midnight.

    Parameters
    ----------
    xrda : xr.DataArray
        xarray.DataArray to extract time from.
    dim_name : str, optional
        Attribute name of the time dimension. The default is "Time".

    Returns
    -------
    np.array
        time in seconds after midnight (dtype float).

    """
    f = attrgetter(dim_name)
    t = f(xrda)

    return (t - t[0].dt.floor("d")).values.astype(int) / 1_000_000_000


###############################################################################


def dtstr_2_mdns(
    timestring: Union[str, list],
    tsfmt: str = "%Y-%m-%d %H:%M:%S.%f",
    ymd: Optional[tuple[int, ...]] = None,
) -> Union[float, list[float]]:
    """
    Convert datetime string to seconds since midnight (float).

    Since a relative difference is calculated, the function is 'timezone-safe'.
    Variable UTC offsets are not allowed.

    Parameters
    ----------
    timestring : str, list of str or np.ndarray with dtype str/obj.
        timestamp given as string.
    tsfmt : str, optional
        timestring format. Pass "iso" to denote ISO8601 format. The default is "%Y-%m-%d %H:%M:%S.%f".
    ymd : tuple, optional
        starting date as tuple of integers; (year, month, day).
        The default is None.

    Returns
    -------
    float; scalar or float; list
        seconds since midnight for the given timestring(s).
    """
    timestring, ret_scalar = _to_list(timestring)

    if tsfmt == "iso":
        dts = [datetime.fromisoformat(s) for s in timestring]
    else:
        dts = [datetime.strptime(s, tsfmt) for s in timestring]

    return dtobj_2_mdns(dts[0] if ret_scalar else dts, ref_date=ymd, ref_is_first=True)


###############################################################################


def dtobj_2_mdns(
    dt_obj: Union[datetime, list[datetime]],
    ref_date: Optional[tuple[int, ...]] = None,
    ref_is_first: bool = False,
) -> Union[float, list[float]]:
    """
    Convert a Python datetime object (or list/array of ...) to seconds after midnight.

    Only a single timezone or no timezone (naive datetime) is allowed.

    Parameters
    ----------
    dt_obj : datetime object or list/array of datetime objects
        the datetime to be converted to seconds after midnight.
    ref_date : tuple of int, optional
        custom start date given as (year, month, day). The default is False.
    ref_is_first : bool, optional
        first entry of dt_obj list/array defines start date.
        The default is False.

    Returns
    -------
    float; scalar or list of float
        seconds after midnight for the given datetime object(s).
    """
    dt_obj, ret_scalar = _to_list(dt_obj)

    tzs = [d.tzinfo for d in dt_obj]
    assert len(set(tzs)) == 1, "all time zones (tzinfo) must be equal."

    t0 = dt_obj[0]
    if ref_date:
        t0 = datetime(*ref_date, tzinfo=dt_obj[0].tzinfo)
    t0 = t0.replace(hour=0, minute=0, second=0, microsecond=0)

    if ref_is_first or ref_date:
        result = [(x - t0).total_seconds() for x in dt_obj]
    else:
        result = [
            (x - x.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            for x in dt_obj
        ]

    return result[0] if ret_scalar else result


###############################################################################


def unixtime_2_mdns(
    timestamp: Union[float, list[float]], ymd: Optional[tuple[int, ...]] = None
) -> Union[float, list[float]]:
    """
    Convert UNIX time (or list/array of ...) to seconds after midnight.

    Parameters
    ----------
    posixts : float, list of float or np.ndarray with dtype float.
        the POSIX timestamp to be converted to seconds after midnight.
    ymd : tuple of int, optional
        define starting date as tuple of integers (year, month, day) UTC.
        The default is None, which means the reference date is that of the
        first element in posixts.

    Returns
    -------
    float; scalar or list of float
        seconds after midnight for the given POSIX timestamp(s).
    """
    timestamps, ret_scalar = _to_list(timestamp)

    # to floor a Unix time to the date, use  t - t % 86400
    # here, we need to account for the fact that the reference date might be different.

    if ymd:  # (yyyy, m, d) given, take that as starting point t0:
        t0 = datetime(year=ymd[0], month=ymd[1], day=ymd[2], tzinfo=timezone.utc).timestamp()
    else:  # take date of first entry as starting point
        t0 = datetime.fromtimestamp(timestamps[0], tz=timezone.utc)
        t0 = t0.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    ts = [t - t0 for t in timestamps]

    return ts[0] if ret_scalar else ts


###############################################################################


def mdns_2_dtobj(
    mdns: Union[float, list[float]],
    ref_date: tuple[int],
    assume_UTC: bool = True,
    posix: bool = False,
    str_fmt: str = "",
) -> Union[datetime, list[datetime]]:
    """
    Convert seconds after midnight (or list/array of ...) to datetime object.

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
    mdns, ret_scalar = _to_list(mdns)
    # ensure type float:
    if not isinstance(mdns[0], (float, np.floating)):
        mdns = list(map(float, mdns))

    # check if ref_date is supplied as a y/m/d tuple. convert to datetime.
    reset_tz = False
    if isinstance(ref_date, (tuple, list)):
        ref_date, reset_tz = datetime(*ref_date), True
        if assume_UTC:  # add timezone UTC if assume_UTC is set to True
            ref_date = ref_date.replace(tzinfo=timezone.utc)

    result = [ref_date + timedelta(seconds=t) for t in mdns]

    if posix:
        if not ref_date.tzinfo:
            print(
                "*mdns_2_dtobj warning*: creating POSIX timestamps from "
                "naive datetime objects might give unexpected results!\n"
                "\t-> consider passing a tz-aware ref_date instead."
            )
        result = [dtobj.timestamp() for dtobj in result]
    elif str_fmt:
        offset = -3 if str_fmt.endswith("%f") else None
        result = [dtobj.strftime(str_fmt)[:offset] for dtobj in result]
    else:
        if reset_tz:
            result = [t.replace(tzinfo=None) for t in result]

    return result[0] if ret_scalar else result


###############################################################################


def daysSince_2_dtobj(
    day0: datetime, days_since: Union[int, float]
) -> Union[datetime, list[datetime]]:
    """
    Convert a date and a floating point number "days_since" to a datetime object.

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
    if isinstance(days_since, (list, np.ndarray)):
        return [(day0 + timedelta(days=ds)) for ds in days_since]
    return day0 + timedelta(days=days_since)


###############################################################################


def dtstr_2_unixtime(
    timestring: str, tsfmt: str = "%Y-%m-%d %H:%M:%S.%f", tz: timezone = timezone.utc
) -> float:
    """
    Convert timestring without time zone information to Unix time.

    Parameters
    ----------
    timestring : string
        representing date (and time).
    tsfmt : str, optional
        strptime format. The default is "%Y-%m-%d %H:%M:%S.%f".
        Set to 'iso' to use Python's datetime.fromisoformat() method.
    tz : timezone, optional
        The default is timezone.utc for UTC.
        Set to None to ignore/use tzinfo as parsed.
        Note: if tzinfo is None after parsing, and tz argument is None,
            Python will assume local time by default!

    Returns
    -------
    POSIX timestamp / UNIX time
        UTC seconds since the Unix epoch 1970-01-01.
    """
    if tsfmt == "iso":
        dtobj = datetime.fromisoformat(timestring)
    else:
        dtobj = datetime.strptime(timestring, tsfmt)

    # if parsed dtobj neither has tzinfo nor utcoffset defined...
    if dtobj.tzinfo is None and dtobj.utcoffset() is None:
        if tz:  # set the tzinfo if tz argument is provided
            dtobj = dtobj.replace(tzinfo=tz)
        else:  # issue a warning if tz argument is None
            warnings.warn(
                "Warning: ambiguous datetime - parsed datetime object won't have tzinfo set!"
            )
    # else the dtobj already has a tz, so convert if tz argument is given:
    else:
        if tz:
            dtobj = dtobj.astimezone(tz)

    return dtobj.timestamp()


###############################################################################
