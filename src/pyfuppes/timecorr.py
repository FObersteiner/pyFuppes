# -*- coding: utf-8 -*-
r"""
Created on Tue Nov 19 14:32:12 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import numpy as np


###############################################################################


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
    parms = np.polyfit(t, t-t_ref, fitorder)
    t_corr = t - np.polyval(parms, t)
    return {'fitparms': parms, 't_corr': t_corr}

#------------------------------------------------------------------------------

def get_tcorr_parms(t, t_ref, fitorder):
    """
    see time_correction(); fit parameter calculation part.
    """
    return np.polyfit(t, t-t_ref, fitorder)

#------------------------------------------------------------------------------

def apply_tcorr_parms(t, parms):
    """
    see time_correction(); fit evaluation part.
    """
    return t - np.polyval(parms, t)


###############################################################################


if __name__ == '__main__':
    ### TESTING

    ## principle
    from matplotlib import pyplot as plt
    order = 1
    t = np.array([1,2,3,4,5,6], dtype=np.float32)
    ref = np.array([1,3,5,7,9,11], dtype=np.float32)
    parms = np.polyfit(t, t-ref, order)
    t_corr = t - np.polyval(parms, t)
    plt.plot(t, 'r', label='t')
    plt.plot(ref, 'b', label='ref', marker='x')
    plt.plot(t_corr, '--k', label='corrected')
    plt.plot(t-ref, 'g', label='delta (t-ref)')
    plt.legend()
