# -*- coding: utf-8 -*-
r"""
Created on Tue Nov 19 14:32:12 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

from copy import deepcopy

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


###############################################################################


def get_tcorr_parms(t, t_ref, fitorder):
    """
    see time_correction(); fit parameter calculation part.
    """
    try:
        parms = np.polyfit(t, t-t_ref, fitorder)
    except np.linalg.LinAlgError: # sometimes happens at first try...
        parms = np.polyfit(t, t-t_ref, fitorder)
    return parms

#------------------------------------------------------------------------------

def apply_tcorr_parms(t, parms):
    """
    see time_correction(); fit evaluation part.
    """
    return t - np.polyval(parms, t)

#------------------------------------------------------------------------------

def time_correction(t, t_ref, fitorder):
    """
    fit a polynomial to the delta between a time vector and a
        reference time vector.
    time vector is corrected by subtracting the evaluated polynomial at each
        point of the time vector.
    inputs:
        t - time vector, 1D np array, numeric type
        t_ref - reference time vector, of same shape as t
        fitorder - order of the polynomial fit, integer

    returns:
        dict, holding
            'fitparms': parameters of the fit, ndarray
            't_corr': corrected input time vector t
    """
    parms = get_tcorr_parms(t, t_ref, fitorder)
    t_corr = apply_tcorr_parms(t, parms)
    return {'fitparms': parms, 't_corr': t_corr}


###############################################################################


def xcorr_timelag(x1, y1, x2, y2,
                  sel_xrange, xunit, to_freq,
                  rmv_NaN=True,
                  pad_to_zero=True,
                  normalize_y=True,
                  show_plots=True, ynames=('y1', 'y2'),
                  corrmode='auto',
                  boundaries=None):
    """
    analyze time lag between two time series by cross-correlation.
    https://en.wikipedia.org/wiki/Cross-correlation#Time_delay_analysis

    Parameters
    ----------
    x1, y1 : 1d arrays
        independend and dependent variable of reference data.
    x2, y2 : 1d arrays
        independend and dependent variable of data to check for time lag.
    sel_xrange : tuple
        cut data to fall within x-range "sel_xrange".
    xunit : numeric, scalar value
        unit of x, seconds.
    to_freq : numeric, scalar value
        interpolate data to frequency "to_freq".
    rmv_NaN : boolean, optional
        clean NaNs from data. The default is True.
    pad_to_zero : boolean, optional
        drag the minimum of y to zero. The default is True.
    normalize_y : boolean, optional
        normalize y data to 0-1. The default is True.
    show_plots : boolean, optional
        show result plot. The default is True.
    corrmode : string, optional. values: 'auto', 'positive', 'negative'
         type of correlation between y1 and y2. The default is auto.
    boundaries: 2-element tuple. lower and upper boundary.
        expect timelag to fall within these boundaries. The default is None.

    Returns
    -------
    scalar value, delay in specified xunit.
    """
    # copy x and y so that nothing gets messed up
    x1, y1 = deepcopy(x1.astype(np.float)), deepcopy(y1.astype(np.float))
    x2, y2 = deepcopy(x2.astype(np.float)), deepcopy(y2.astype(np.float))

    # cut to selected xrange:
    m1 = (x1 >= sel_xrange[0]) & (x1 < sel_xrange[1])
    x1, y1 = x1[m1], y1[m1]
    m2 = (x2 >= sel_xrange[0]) & (x2 < sel_xrange[1])
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

    if show_plots:
        fig, ax = plt.subplots(2,1, figsize=(14,10))
        plt.subplots_adjust(top=0.94, bottom=0.06, left=0.06, right=0.94)
        p0 = ax[0].plot(x1, y1, 'r', label=f"{ynames[0]}")
        ax[0].set_xlabel("x", weight='bold')
        ax[0].set_ylabel(f"{ynames[0]} normalized")
        ax[0].set_title("input")
        ax1 = ax[0].twinx()
        p1 = ax1.plot(x2, y2, 'b', label=f"{ynames[1]}")
        ax1.set_ylabel(f"{ynames[1]} normalized")

    # normalize x:
    start, end = np.floor(x1[0]), np.ceil(x1[-1])
    n = (end-start)*to_freq
    xnorm = np.linspace(start, end, num=int(n), endpoint=False)

    # interpolate y1 and y2 to xnorm:
    f_ip = interp1d(x1, y1, kind='linear', bounds_error=False,
                    fill_value="extrapolate")
    y1res = f_ip(xnorm)
    f_ip = interp1d(x2, y2, kind='linear', bounds_error=False,
                    fill_value="extrapolate")
    y2res = f_ip(xnorm)

    if show_plots:
        p2 = ax[0].plot(xnorm, y1res, 'firebrick', label=f"{ynames[0]} resampled")
        p3 = ax1.plot(xnorm, y2res, 'deepskyblue', label=f"{ynames[1]} resampled")
        plots = p0 + p1 + p2 + p3
        lbls = [l.get_label() for l in plots]
        ax[0].legend(plots, lbls, loc=0, framealpha=1, facecolor='white')

    # cross-correlate y2 vs. y1 and normalize to 0-1:
    corr = (np.correlate(y2res, y1res, mode='same') /
            np.sqrt(np.correlate(y1res, y1res, mode='same')[int(n/2)] *
                    np.correlate(y2res, y2res, mode='same')[int(n/2)]))

    delay_arr = np.linspace(-0.5*n/to_freq, 0.5*n/to_freq, int(n))

    if boundaries:
        m = (delay_arr >= boundaries[0]) & (delay_arr < boundaries[1])
        delay_arr = delay_arr[m]
        corr = corr[m]

    # check if correlation is positive or negative to determine lag time
    funcs = (np.argmin, np.argmax)
    if corrmode == 'auto':
        select = funcs[int(np.ceil(np.corrcoef(y2res, y1res)[0,1]))]
    elif corrmode == 'positive':
        select = funcs[1]
    elif corrmode == 'negative':
        select = funcs[0]

    delay = delay_arr[select(corr)]

    if show_plots:
        ax[1].plot(delay_arr, corr, 'k', label='xcorr')
        ax[1].axvline(x=delay, color='r', linewidth=2)
        ax[1].set_xlabel('lag')
        ax[1].set_ylabel('correlation coefficient')
        ax[1].set_title(f"{ynames[1]} vs. {ynames[0]} lag: {delay:+.3f}")

    return delay


###############################################################################


if __name__ == '__main__':
    # illustration of time_correction():
    order = 1
    t = np.array([1,2,3,4,5,6], dtype=float)
    ref = np.array([1,3,5,7,9,11], dtype=float)
    parms = np.polyfit(t, t-ref, order)
    t_corr = t - np.polyval(parms, t)
    plt.plot(t, 'r', label='t')
    plt.plot(ref, 'b', label='ref', marker='x')
    plt.plot(t_corr, '--k', label='corrected')
    plt.plot(t-ref, 'g', label='delta (t-ref)')
    plt.legend()