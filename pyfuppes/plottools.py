# -*- coding: utf-8 -*-
"""Helpers to format plots."""

import numpy as np


###############################################################################


def get_plot_range(
    v, add_percent=5, v_min_lim=None, v_max_lim=None, xrange=None, x=None
):
    """
    Adjust y-axis range of matplotlib pyplot for a given vector v.

    Parameters
    ----------
    v : list or numpy 1d array
        dependent variable.
    add_percent : numeric type scalar value, optional
        percent of the range of v that should be added to result. The default is 5.
    v_min_lim : numeric type scalar value, optional
        minimum value for lower yrange limit. The default is False.
    v_max_lim : numeric type scalar value, optional
        maximum value for upper yrange limit. The default is False.
    xrange : list, optional
        [lower_limit, upper_limit] of independent variable. The default is False.
    x : list or numpy 1d array, optional
        independent variable. The default is False.

    Returns
    -------
    result : list
        lower and upper limit.

    """
    if hasattr(v, "mask"):  # numpy masked array: only use non-masked values
        v = v[~v.mask]

    if not isinstance(v, np.ndarray):
        v = np.array(v)  # ensure array type

    if x is not None and xrange is not None:
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        x = np.sort(x)  # monotonically increasing x-vector (e.g. time)
        if len(x) == len(v):
            w_xvd = (x >= xrange[0]) & (x <= xrange[1])
            v = v[w_xvd]

    v = v[np.isfinite(v)]

    if len(v) < 2:
        # it is better not to raise an exception in case no valid input,
        # to avoid errors further down...
        return [-1, 1]

    v_min, v_max = v.min(), v.max()
    offset = (abs(v_min) + abs(v_max)) / 2 * add_percent / 100
    result = [v_min - offset, v_max + offset]

    if v_min_lim:
        if result[0] < v_min_lim:
            result[0] = v_min_lim

    if v_max_lim:
        if result[1] > v_max_lim:
            result[1] = v_max_lim

    return result


###############################################################################


def nticks_yrange(yrange, nticks, to_multiples_of=10):
    """
    Update a plot yrange so that it fits nicely into a certain number of ticks.

    Parameters
    ----------
    yrange : 2-element tuple or list
        the yrange to modify.
    nticks : int
        number of ticks along y-axis.
    to_multiples_of : int, optional
        make the yrange divisible w/o remainder by .... The default is 10.

    Returns
    -------
    result : 2-element list
        updated yrange.

    """
    result = [
        np.floor(yrange[0] / to_multiples_of) * to_multiples_of,
        np.ceil(yrange[1] / to_multiples_of) * to_multiples_of,
    ]

    size = np.lcm(nticks - 1, to_multiples_of)
    n, r = divmod((result[1] - result[0]), size)

    add = 1 if r > to_multiples_of else 0
    result[1] = result[0] + (n + add) * size

    return result


###############################################################################
