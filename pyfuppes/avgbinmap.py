# -*- coding: utf-8 -*-
"""Averaging, Binning, Mapping."""

from cmath import phase, rect
from copy import deepcopy
from math import atan2, cos, degrees, pi, radians, sin
from typing import NamedTuple, Optional, Union

import numpy as np
import pandas as pd
from numba import njit
from scipy.interpolate import interp1d
from scipy.ndimage import uniform_filter1d
from scipy.stats import circmean

###############################################################################


def mean_angle(deg: Union[list, np.ndarray, np.ma.masked_array]) -> float:
    """
    Calculate a mean angle.

    input:
        deg - (list or array) values to average

    notes:
        - if input parameter deg contains NaN or is a numpy masked array, missing
          values will be removed before the calculation.
        - result is degrees between -180 and +180.

    Returns
    -------
        mean of deg (float)
    """
    if isinstance(deg, np.ma.masked_array):
        deg = deg.data
    elif isinstance(deg, np.ndarray):
        deg = deg[np.isfinite(deg)]

    if len(deg) == 0:
        return np.nan
    elif len(deg) == 1:
        return deg[0]

    return degrees(phase(sum(rect(1, radians(d)) for d in deg) / len(deg)))


###############################################################################


@njit
def mean_angle_numba(angles: np.ndarray) -> float:
    """
    mean_angle(), numba-JIT compiled.

    - input must be numpy array of type float!

    C version: https://rosettacode.org/wiki/Averages/Mean_angle
    """
    angles = angles[np.isfinite(angles)]
    if len(angles) == 0:
        return np.nan
    elif len(angles) == 1:
        return angles[0]

    size = len(angles)
    y_part = 0.0
    x_part = 0.0

    for i in range(size):
        x_part += cos(angles[i] * pi / 180)
        y_part += sin(angles[i] * pi / 180)

    return atan2(y_part / size, x_part / size) * 180 / pi


###############################################################################


def mean_angle_sc(deg: np.ndarray) -> float:
    """
    scipy.stats.circmean-based version of mean_angle().
    """
    if len(deg) == 0:
        return np.nan
    if len(deg) == 1:
        return deg[0]

    result = np.rad2deg(circmean(np.deg2rad(deg), nan_policy="omit"))
    if np.isclose(result, 0):
        return 0.0

    if result > 180:  # map to +-180 for consistency with other functions
        result -= 360

    return float(result)


###############################################################################


def mean_day_frac(
    dfr: Union[list, np.ndarray, np.ma.masked_array], use_numba: bool = True
) -> float:
    """
    Calculate a mean day fraction (0-1) with mean_angle function.

    the conversion to angle is necessary since day changes cannot be
      calculated as arithmetic mean.
    - dfr: day fraction, 0-1
    - if input parameter dfr contains NaN or is a numpy masked array, missing
      values will be removed before the calculation.
    """
    if isinstance(dfr, np.ma.masked_array):
        _dfr = dfr.data
    elif isinstance(dfr, np.ndarray):
        _dfr = dfr[np.isfinite(dfr)]
    else:
        _dfr = np.array(dfr, dtype=float)
        _dfr = _dfr[np.isfinite(_dfr)]

    # _dfr is now guaranteed to be of np.ndarray

    if len(_dfr) == 0:
        return np.nan
    elif len(_dfr) == 1:
        return _dfr[0]

    deg_mean = mean_angle_numba(_dfr * 360) if use_numba else mean_angle(_dfr * 360)

    if np.isclose(deg_mean, 0):
        return 0.0

    if deg_mean < 0:  # account for mean angle between -180 and +180
        deg_mean += 360

    return deg_mean / 360


###############################################################################

TimeBins = NamedTuple(
    "bin_data",
    [
        ("t_binned", np.ndarray),
        ("bins", np.ndarray),
        ("masked_bins", np.ndarray),
        ("masked_vals", np.ndarray),
    ],
)


def bin_t_10s(t: np.ndarray, force_t_range: bool = True, drop_empty: bool = True) -> TimeBins:
    """
    Bin a time axis to 10 s intervals around 5.

    Lower boundary included, upper boundary excluded (0. <= 5. < 10.).

    input:
        t - np.ndarray (time vector, unit=second, increasing monotonically)
    keywords:
        force_t_range (bool) - True enforces bins to fall within range of t
        drop_empty (bool) - False keeps empty bins alive

    Returns
    -------
        dict with binned time axis and bins, as returned by np.searchsorted()
    """
    if t.ndim != 1:
        raise TypeError("Please pass 1D array to function.")

    from pyfuppes.monotonicity import strict_inc_np

    if not strict_inc_np(t):
        raise ValueError("Input must be strictly increasing.")

    tmin, tmax = np.floor(t[0]), np.floor(t[-1])
    t_binned = np.arange((tmin - tmin % 10) + 5, (tmax - tmax % 10) + 6, 10)

    # if all values of t should fall WITHIN the range of t_binned:
    vmask = np.array([], dtype=bool)
    if force_t_range:
        if t_binned[0] < t[0]:
            t_binned = t_binned[1:]
        if t_binned[-1] > t[-1]:
            t_binned = t_binned[:-1]
        # check if values should be masked, e.g. if an element in t does not
        # fall into the bins
        vmask = (t < t_binned[0] - 5) | (t >= t_binned[-1] + 5)
        t = t[~vmask]

    bins = np.searchsorted(t_binned - 5, t, side="right")

    # if empty bins should be created, mask all bins that would have no
    # corresponding value in the dependent variable's data
    bmask = np.array([], dtype=bool)
    if drop_empty:
        t_binned = t_binned[np.bincount(bins - 1).astype(np.bool_)]
    else:
        bmask = np.ones(t_binned.shape).astype(np.bool_)
        bmask[bins - 1] = False

    return TimeBins(
        t_binned,
        bins,
        bmask,
        vmask,
    )


###############################################################################


@njit
def get_npnanmean(v: np.ndarray):
    """nan-mean, numba-JIT compiled."""
    return np.nanmean(v)


def bin_y_of_t(
    v: np.ndarray,
    bin_info: TimeBins,
    vmiss: float = np.nan,
    aggregation: str = "mean",
    use_numba: bool = True,
) -> np.ndarray:
    """
    Use the output of function "bin_time" or "bin_time_10s" to bin a variable 'v' that depends on a variable t.

    input:
        v - np.ndarray to be binned
        bin_info - config dict returned by bin_time() or bin_time_10s()
    keywords:
        vmiss (numeric) - missing value identifier, defaults to np.nan
        return_type (str) - how to bin, defaults to 'mean'. Options:
            'mean' - arithmetic mean
            'mean_day_frac' - mean of fractional day
            'mean_angle' - mean of angle
        use_numba (bool) - use njit'ed binning functions or not

    Returns
    -------
        v binned according to parameters in bin_info
    """
    if not any(
        v.dtype == np.dtype(t) for t in ("int16", "int32", "int64", "float16", "float32", "float64")
    ):
        raise TypeError("Please pass valid dtype, int or float.")

    # make a deep copy so that v is not modified on the way
    _v = deepcopy(v)

    # change dtype to float so we can use NaN
    if any(_v.dtype == np.dtype(t) for t in ("int16", "int32", "int64")):
        _v = _v.astype(float)

    _v[_v == vmiss] = np.nan

    # remove values that were masked (out of bin range)
    _v = _v[~bin_info.masked_vals]

    v_binned = []
    vd_bins = bin_info.bins

    if aggregation == "mean":
        if use_numba:
            v_binned = [get_npnanmean(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
        else:
            v_binned = [np.nanmean(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
            #
            # another option from <https://codereview.stackexchange.com/a/294677/206249>:
            #
            # _, inverse, counts = np.unique(vd_bins, return_inverse=True, return_counts=True)
            # v_binned = np.bincount(inverse, weights=_v) / counts
            #
    elif aggregation == "mean_day_frac":
        if use_numba:
            v_binned = [mean_day_frac(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
        else:
            v_binned = [
                mean_day_frac(_v[vd_bins == bin_no], use_numba=False)
                for bin_no in np.unique(vd_bins)
            ]
    elif aggregation == "mean_angle":
        if use_numba:
            v_binned = [mean_angle_numba(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]
        else:
            v_binned = [mean_angle(_v[vd_bins == bin_no]) for bin_no in np.unique(vd_bins)]

    result = np.array(v_binned)

    # check if there are masked bins, i.e. empty bins. add them to the output if so.
    if bin_info.masked_bins.shape[0] > 0:
        tmp = np.ones(bin_info.masked_bins.shape)
        tmp[bin_info.masked_bins] = vmiss
        tmp[~bin_info.masked_bins] = result
        result = tmp

    # round to integers if input type was integer
    if any(v.dtype == np.dtype(t) for t in ("int16", "int32", "int64")):
        result = np.rint(result).astype(v.dtype)

    return result


###############################################################################


def bin_by_pdresample(
    t: np.ndarray,
    v: np.ndarray,
    t_unit: str = "s",
    rule: str = "10s",
    offset: Optional[pd.Timedelta] = pd.Timedelta(seconds=5),  # type: ignore
    force_t_range: bool = True,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """
    Use pandas DataFrame method "resample" for binning along a time axis.

    Can only sample down, see also https://stackoverflow.com/q/66967998/10197418.

    Parameters
    ----------
    t : 1d array of float or int
        time axis / independent variable. unit: see keyword 't_unit'.
    v : 1d or 2d array corresponding to t
        dependent variable(s).
    rule : string, optional
        rule for resample method. The default is '10S'.
    offset : datetime.timedelta, optional
        offset to apply to the starting value.
        The default is timedelta(seconds=5).
    force_t_range : boolean, optional
        truncate new time axis to min/max of t. The default is True.
    drop_empty : boolean, optional
        drop empty bins that otherwise hold NaN. The default is True.

    Returns
    -------
    pandas DataFrame
        data binned (arithmetic mean) to resampled time axis.
    """
    d = {f"v_{i}": y for i, y in enumerate(v)} if isinstance(v, list) else {"v_0": v}

    df = pd.DataFrame(d, index=pd.to_datetime(t, unit=t_unit))
    df = df.resample(rule).mean()
    if offset:
        df.index = df.index + pd.tseries.frequencies.to_offset(offset)

    df["t_binned"] = df.index.values.astype(np.int64) / 10**9

    if force_t_range:
        if df["t_binned"].iloc[0] < t[0]:
            df = df.drop(df.index[0])
        if df["t_binned"].iloc[-1] > t[-1]:
            df = df.drop(df.index[-1])

    df = df.drop(columns=["t_binned"]).set_index(df["t_binned"])

    if drop_empty:
        df = df.dropna(how="all")

    return df


###############################################################################


def bin_by_npreduceat(v: np.ndarray, nbins: int, ignore_nan: bool = True) -> np.ndarray:
    """
    Bin with numpy.add.reduceat (1D).

    ignores NaN or INF by default (finite elements only).
    if ignore_nan is set to False, the whole bin will be NaN if 1 or more NaNs
        fall within the bin.
    """
    bins = np.linspace(0, v.size, nbins + 1, True).astype(int)

    if ignore_nan:
        mask = np.isfinite(v)
        vn = np.where(~mask, 0, v)
        with np.errstate(invalid="ignore"):
            out = np.add.reduceat(vn, bins[:-1]) / np.add.reduceat(mask, bins[:-1])
    else:
        out = np.add.reduceat(v, bins[:-1]) / np.diff(bins)

    return out


###############################################################################


def np_mvg_avg(
    v: np.ndarray,
    N: int,
    ip_ovr_nan: bool = False,
    mode: str = "same",
    expand_edges: bool = True,
) -> np.ndarray:
    """
    Calculate moving average based on numpy convolution function.

    Parameters
    ----------
    v : 1d array
        data to average.
    N : integer
        number of samples per average.
    ip_ovr_nan : boolean, optional
        interpolate linearly using finite elements of v. The default is False.
    mode : string, optional
        config for np.convolve. The default is 'same'.
    expand_edges : bool, optional
        in case of mode='same', convolution gives incorrect results
        ("running-in effect") at edges. account for this by
        simply expanding the Nth value to the edges.

    Returns
    -------
    m_avg : 1d array
        averaged data.
    """
    if ip_ovr_nan:
        x = np.linspace(0, len(v) - 1, num=len(v))
        fip = interp1d(
            x[np.isfinite(v)],
            v[np.isfinite(v)],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",  # type: ignore
        )
        v = fip(x)

    m_avg = np.convolve(v, np.ones((N,)) / N, mode=mode)  # type: ignore

    if expand_edges:
        m_avg[: N - 1], m_avg[-N:] = m_avg[N - 1], m_avg[-N]

    return m_avg


###############################################################################


def pd_mvg_avg(
    v: Union[list, np.ndarray], N: int, ip_ovr_nan: bool = False, min_periods: int = 1
) -> np.ndarray:
    """
    Calculate moving average based on pandas dataframe rolling function.

    Parameters
    ----------
    v : 1d array
        data to average.
    N : integer
        number of samples per average.
    ip_ovr_nan : boolean, optional
        interpolate linearly using finite elements of v. The default is False.
    min_periods : TYPE, optional
        minimum number of values in averaging window. The default is 1.

    NOTE: automatically skips NaN (forms averages over windows with <N),
          unless minimum number of values in window is exceeded.

    Returns
    -------
    1d array
        averaged data.
    """
    N, min_periods = int(N), int(min_periods)

    min_periods = 1 if min_periods < 1 else min_periods

    df = pd.DataFrame({"v": v})
    df["rollmean"] = df["v"].rolling(int(N), center=True, min_periods=min_periods).mean()
    if ip_ovr_nan:
        df["ip"] = df["rollmean"].interpolate()
        return df["ip"].values  # type: ignore

    return df["rollmean"].values  # type: ignore


###############################################################################


def sp_mvg_avg(v: np.ndarray, N: int, edges: str = "nearest") -> np.ndarray:
    """
    Use scipy's uniform_filter1d to calculate a moving average.

    See the docs at
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.uniform_filter1d.html
    Handles NaNs by removing them before interpolation.

    Parameters
    ----------
    v : np.ndarray
        data to average.
    N : int
        number of samples per average.
    edges : str, optional
        mode of uniform_filter1d (see docs at link above). The default is 'nearest'.
        {‘reflect’, ‘constant’, ‘nearest’, ‘mirror’, ‘wrap’}

    Returns
    -------
    avg : np.ndarray
        averaged data.
    """
    m = np.isfinite(v)
    avg = np.empty(v.shape)
    avg[~m] = np.nan
    avg[m] = uniform_filter1d(v[m], size=N, mode=edges)

    return avg


###############################################################################


def map_dependent(
    xref: np.ndarray, xcmp: np.ndarray, vcmp: np.ndarray, vmiss: float = np.nan
) -> np.ndarray:
    """
    Map a variable "vcmp" depending on variable "xcmp" to an independent variable "xref".

    Parameters
    ----------
    xref : np.ndarray, 1D
        reference / independent variable.
    xcmp : np.ndarray, 1D
        independent variable of vcmp.
    vcmp : np.ndarray, 1D
        dependent variable of xcmp.
    vmiss : int or float
        what should be inserted to specify missing values.

    Returns
    -------
    vmap : np.ndarray, 1D
        vcmp mapped to xref.
    """
    # which element of xref has a corresponding element in xcmp?
    m = np.isin(xref, xcmp)

    # prepare output
    vmap = np.empty(xref.shape, dtype=vcmp.dtype)
    # insert VMISS where xref has NO corresponding element
    vmap[~m] = vmiss

    # where corresponding elements exist, insert those from vcmp
    vmap[m] = np.take(vcmp, np.nonzero(np.isin(xcmp, xref)))[0]

    return vmap


###############################################################################


@njit
def calc_shift(
    arr: np.ndarray,
    step: float = 1,
    lower_bound: float = -2,
    upper_bound: float = 3,
    _tol: float = 1e-9,
) -> np.ndarray:
    """
    Calculate shift-values that, when added to arr, put the values of arr on a regular grid. Code gets numba-JIT compiled.

    Parameters
    ----------
    arr : np.ndarray
        irregularly gridded numbers.
    step : float, optional
        step size to expect in a regular grid. The default is 1.
    lower_bound : float, optional
        shift lower bound, included. The default is-2.
    upper_bound : float, optional
        shift upper bound, excluded. The default is 3.
    _tol : float, optional
        tolerance for divisibility check. The default is 1e-9.

    Returns
    -------
    shift : np.ndarray
        array with shift values.

    """
    shift = np.zeros(arr.shape[0])
    # first element of arr must be evenly divisible by step, otherwise the first
    # element of shift must account for that
    m = arr[0] % step
    dy = abs(step - m)
    if not (m < _tol or dy < _tol):
        shift[0] = -(arr[0] % step)

    for i, v in enumerate(arr[1:]):
        offset = (arr[i] - v + shift[i]) + step
        if offset < lower_bound or offset >= upper_bound:
            offset = 0
        shift[i + 1] = offset

    return shift


###############################################################################
