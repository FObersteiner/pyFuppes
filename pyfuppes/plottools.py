# -*- coding: utf-8 -*-
r"""
Created on Mon Aug 20 13:36:57 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import numpy as np


###############################################################################


def get_plot_range(v, add_percent=5,
                   v_min_lim=False, v_max_lim=False,
                   xrange=False, x=False):
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
    v = np.array(v, dtype=np.float) # ensure array type

    if x and xrange:
        x = np.sort(np.array(x)) # monotonically increasing x-vector (e.g. time)
        if len(x) == len(v):
            w_xvd = ((x >= xrange[0]) & (x <= xrange[1]))
            v = v[w_xvd]

    v = v[np.isfinite(v)]

    if len(v) < 2:
        raise ValueError("input must at least contain 2 elements")

    v_min, v_max = v.min(), v.max()
    offset = (abs(v_min)+abs(v_max))/2 * add_percent/100
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
    update a plot yrange so that it fits nicely into a certain number of
    ticks

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

    result = [np.floor(yrange[0]/to_multiples_of)*to_multiples_of,
              np.ceil(yrange[1]/to_multiples_of)*to_multiples_of]

    size = np.lcm(nticks-1, to_multiples_of)
    n, r = divmod((result[1]-result[0]), size)

    add = 1 if r > to_multiples_of else 0
    result[1] = result[0] + (n + add)*size

    return result


###############################################################################
