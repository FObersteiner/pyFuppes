# -*- coding: utf-8 -*-
"""Corrections for time in timeseries data."""

import functools
from copy import deepcopy
from datetime import timedelta
from typing import Callable, NamedTuple, Optional

import numpy as np
import polars as pl
import scipy as sc
from matplotlib import pyplot as plt

###############################################################################

CorrTime = NamedTuple(
    "corrected_time",
    [
        ("fitparms", np.ndarray),
        ("t_corr", np.ndarray),
    ],
)


def correct_time(t: np.ndarray, t_ref: np.ndarray, fitorder: int) -> CorrTime:
    """
    Fit a polynomial to the delta between a time vector and a reference time vector.

    time vector is corrected by subtracting the evaluated polynomial at each
        point of the time vector.
    inputs:
        t - time vector, 1D np array, numeric type
        t_ref - reference time vector, of same shape as t
        fitorder - order of the polynomial fit, integer

    Returns
    -------
        dict, holding
            'fitparms': parameters of the fit, ndarray
            't_corr': corrected input time vector t
    """
    try:
        parms = np.polyfit(t, t - t_ref, fitorder)
    except np.linalg.LinAlgError:  # sometimes happens at first try...
        parms = np.polyfit(t, t - t_ref, fitorder)
    t_corr = t - np.polyval(parms, t)

    return CorrTime(parms, t_corr)


###############################################################################

FilteredDt = NamedTuple(
    "filtered_dt",
    [
        ("n", int),
        ("df", pl.DataFrame),
    ],
)


def filter_dt_forward(df: pl.DataFrame, datetime_key: str = "datetime") -> FilteredDt:
    """
    Given a time series as polars.DataFrame, ensure that the index is increasing strictly.

    Filters forwards, i.e. if one element is less than the previous, then this
    element is removed (not the previous).

    Parameters
    ----------
    df : polars DataFrame
        DataFrame with datetime index.
    datetime_key : str, optional
        Date/time column name. The default is "datetime".

    Returns
    -------
    (n, df) : (int, polars DataFrame)
        The number of removed columns and the filtered dataframe.
    """
    fill_value = timedelta(microseconds=1)
    ref_value = timedelta(0)
    n_removed = 0

    m = df[datetime_key].diff().fill_null(fill_value) > ref_value
    while not m.all():
        if df.height == 1:
            return (int(n_removed), df)
        df = df.filter(m)
        n_removed += (~m).sum()
        m = df[datetime_key].diff().fill_null(fill_value) > ref_value

    return FilteredDt(int(n_removed), df)


# -----------------------------------------------------------------------------


def filter_dt_backward(df: pl.DataFrame, datetime_key: str = "datetime") -> FilteredDt:
    """
    As filter_dt_forward, but backwards filtering.

    If one element is less than the previous, then the previous element is removed.
    """
    fill_value = timedelta(microseconds=1)
    ref_value = timedelta(0)
    n_removed = 0

    m = (df[datetime_key].diff().fill_null(fill_value) > ref_value).shift(-1).fill_null(True)
    while not m.all():
        if df.height == 1:
            return (int(n_removed), df)
        df = df.filter(m)
        n_removed += (~m).sum()
        m = (df[datetime_key].diff().fill_null(fill_value) > ref_value).shift(-1).fill_null(True)

    return FilteredDt(int(n_removed), df)


###############################################################################


def xcorr_timelag(
    x1: np.ndarray,
    y1: np.ndarray,
    x2: np.ndarray,
    y2: np.ndarray,
    xrange: Optional[tuple[float, float]] = None,
    upscale: int = 100,
    rmv_NaN: bool = True,
    pad_to_zero: bool = True,
    normalize_y: bool = True,
    # detrend_y=True, # possible future feature
    show_plots: bool = True,
    ynames: tuple[str, str] = ("f", "g"),
    corrmode: str = "positive",
    boundaries: Optional[tuple[float, float]] = None,
    xcorr_func: Callable = sc.signal.correlate,
) -> float:
    """
    Analyze time lag between two time series f and g by cross-correlation.

    https://en.wikipedia.org/wiki/Cross-correlation#Time_delay_analysis

    a positive lag of g vs. f (reference) means that g lags behind in time.
    vice versa, if the lag is negative, g's signal preceedes that of f in time.

    Parameters
    ----------
    x1, y1 : 1d arrays
        independend and dependent variable of reference data.
    x2, y2 : 1d arrays
        independend and dependent variable of data to check for time lag.
    xrange : tuple, optional.
        cut data to fall within x-range "xrange". The default is (x1.min(), x2.max())
    upscale : numeric, scalar value
        upscale the data frequency by factor of upscale. The default is 100.
    rmv_NaN : boolean, optional
        clean NaNs from data. The default is True.
    pad_to_zero : boolean, optional
        drag the minimum of y to zero. The default is True.
    normalize_y : boolean, optional
        normalize y data to 0-1. The default is True.
    show_plots : boolean, optional
        show result plot. The default is True.
    ynames : tuple of str, optional
        2-element tuple of names to use on the plot. The default is ("f", "g").
    corrmode : str, optional.
        type of correlation to expect between y1 and y2. values: 'auto',
        'positive', 'negative'. The default is "positive".
    boundaries: 2-element tuple. lower and upper boundary.
        expect timelag to fall within these boundaries. The default is None.
    xcorr_func : func, optional
        function to calculate cross-correlation. The default is scipy.signal.correlate.

    Returns
    -------
    delay : float
        time delay of f vs. g in the unit of the input's independent variable.
    """
    # copy x and y so that nothing gets messed up
    x1, y1 = deepcopy(x1.astype(float)), deepcopy(y1.astype(float))
    x2, y2 = deepcopy(x2.astype(float)), deepcopy(y2.astype(float))

    # cut to selected xrange:
    if xrange is None:
        xrange = (x1.min(), x2.max())

    m1 = (x1 >= xrange[0]) & (x1 < xrange[1])
    x1, y1 = x1[m1], y1[m1]
    m2 = (x2 >= xrange[0]) & (x2 < xrange[1])
    x2, y2 = x2[m2], y2[m2]

    if rmv_NaN:
        m1 = np.isfinite(y1)
        y1, x1 = y1[m1], x1[m1]
        m2 = np.isfinite(y2)
        y2, x2 = y2[m2], x2[m2]

    if pad_to_zero:
        y1 -= np.nanmedian(y1)
        y2 -= np.nanmedian(y2)

    # this will fail if either one of the arrays holds no elements:
    if normalize_y:
        y1 /= np.nanmax(y1)
        y2 /= np.nanmax(y2)

    # normalize x:
    start, end = np.floor(x1[0]), np.ceil(x1[-1])
    n = (end - start) * upscale
    xnorm = np.linspace(start, end, num=int(n), endpoint=False)

    # interpolate y1 and y2 to xnorm:
    f_ip = sc.interpolate.interp1d(
        x1, y1, kind="linear", bounds_error=False, fill_value="extrapolate"
    )
    f = f_ip(xnorm)
    f_ip = sc.interpolate.interp1d(
        x2, y2, kind="linear", bounds_error=False, fill_value="extrapolate"
    )
    g = f_ip(xnorm)

    # cross-correlate f vs. g (i.e. y1 vs. y2):
    corr = xcorr_func(f, g)

    # need to know used correl function to make delay array...
    # check first if functools.partial was used.
    usedfunc = xcorr_func.func if xcorr_func.__class__ == functools.partial else xcorr_func  # type: ignore
    # if usedfunc.__code__ == np.correlate.__code__:
    #     delay_arr = np.linspace(-0.5 * n / upscale, 0.5 * n / upscale, int(n))[::-1]
    # elif usedfunc.__code__ == sc.signal.correlate.__code__:
    #     delay_arr = np.arange(1 - xnorm.size, xnorm.size) * (end - start) / xnorm.size * -1
    if usedfunc == np.correlate:
        delay_arr = np.linspace(-0.5 * n / upscale, 0.5 * n / upscale, int(n))[::-1]
    elif usedfunc == sc.signal.correlate:
        delay_arr = np.arange(1 - xnorm.size, xnorm.size) * (end - start) / xnorm.size * -1
    else:
        raise ValueError(f"unknown correl func: {repr(usedfunc)}")

    if boundaries:
        m = (delay_arr >= boundaries[0]) & (delay_arr < boundaries[1])
        delay_arr = delay_arr[m]
        corr = corr[m]

    # check if correlation is positive or negative to determine lag time
    assert corrmode in ("auto", "negative", "positive")
    if corrmode == "negative":
        select = np.argmin
    elif corrmode == "positive":
        select = np.argmax
    else:
        select = (np.argmin, np.argmax)[int(np.ceil(np.corrcoef(f, g)[0, 1]))]

    delay = delay_arr[select(corr)]

    if show_plots:
        _, ax = plt.subplots(2, 1, figsize=(14, 10))
        plt.subplots_adjust(top=0.94, bottom=0.06, left=0.06, right=0.94)
        p0 = ax[0].plot(x1, y1, "r", label=f"{ynames[0]}")
        ax[0].set_xlabel("x", weight="bold")
        ax[0].set_ylabel(f"{ynames[0]} normalized")
        ax[0].set_title("input")
        ax1 = ax[0].twinx()
        p1 = ax1.plot(x2, y2, "b", label=f"{ynames[1]}")
        ax1.set_ylabel(f"{ynames[1]} normalized")
        p2 = ax[0].plot(xnorm, f, "firebrick", label=f"{ynames[0]} resampled")  # type: ignore
        p3 = ax1.plot(xnorm, g, "deepskyblue", label=f"{ynames[1]} resampled")  # type: ignore
        plots = p0 + p1 + p2 + p3  # type: ignore
        lbls = [p.get_label() for p in plots]
        ax[0].legend(plots, lbls, loc=0, framealpha=1, facecolor="white")  # type: ignore
        ax[1].plot(delay_arr, corr, "k", label="xcorr")  # type: ignore
        ax[1].axvline(x=delay, color="r", linewidth=2)  # type: ignore
        ax[1].set_xlabel("lag")  # type: ignore
        ax[1].set_ylabel("correlation coefficient")  # type: ignore
        ax[1].set_title(f"{ynames[1]} vs. {ynames[0]} lag: {delay:+.3f}")  # type: ignore
        plt.show()

    return delay


###############################################################################


if __name__ == "__main__":
    # illustration of time_correction():
    order = 1
    t = np.array([1, 2, 3, 4, 5, 6], dtype=float)
    ref = np.array([1, 3, 5, 7, 9, 11], dtype=float)
    parms = np.polyfit(t, t - ref, order)
    t_corr = t - np.polyval(parms, t)
    plt.plot(t, "r", label="t")
    plt.plot(ref, "b", label="ref", marker="x")
    plt.plot(t_corr, "--k", label="corrected")
    plt.plot(t - ref, "g", label="delta (t-ref)")
    plt.legend()
