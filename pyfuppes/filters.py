# -*- coding: utf-8 -*-
"""Filtering and Masking."""

import numpy as np
from numba import njit
from scipy.interpolate import interp1d

###############################################################################


def mask_repeated(a, N, atol=1e-6):
    """
    Mask elements that repeat more than N times.

    on SO:
        https://stackoverflow.com/a/58482894/10197418

    Parameters
    ----------
    a : 1d array
    N : int
        mask element if it repeats more than n times
    atol : float, optional
        absolute tolerance to check for equality. The default is 1e-6.

    Returns
    -------
    boolean mask

    """
    mask = np.ones(a.shape[0], np.bool_)
    mask[N:] = ~np.isclose(a[N:], a[:-N], atol=atol, equal_nan=True)
    return mask


###############################################################################


@njit
def mask_repeated_nb(arr, n, atol=1e-6):
    """
    Mask elements that repeat more than N times, njit'ed version.

    Parameters
    ----------
    arr : 1d array
    n : int
        mask element if it repeats more than n times
    atol : float, optional
        absolute tolerance to check for equality. The default is 1e-6.

    Returns
    -------
    boolean mask
    """
    mask = np.ones(arr.shape, np.bool_)
    current = arr[0]
    count = 0
    for idx, item in enumerate(arr):
        if abs(item - current) < atol:
            count += 1
        else:
            current = item
            count = 1
        mask[idx] = count <= n
    return mask


###############################################################################


@njit
def mask_jumps(arr, threshold, look_ahead, abs_delta=False):
    """
    Check elements of array "arr" if difference between subsequent elements exceeds threshold.

    Parameters
    ----------
    arr : np.ndarray
        Numpy 1darray to analyze.
    threshold : [float, int]
        Maximum allowed difference between subsequent elements.
    look_ahead : int
        How many elements to look ahead if a difference exceedes threshold.
    abs_delta : bool, optional
        Consider the absolute difference. The default is False.

    Returns
    -------
    mask : np.ndarray
        Boolean mask.
    """
    n_el = arr.shape[0]
    mask = np.ones(arr.shape).astype(np.bool_)
    i = 0
    while i < n_el - 1:
        cur, nxt = arr[i], arr[i + 1]
        delta_0 = np.absolute(nxt - cur) if abs_delta else nxt - cur
        if delta_0 > threshold:
            for value in arr[i + 1 : i + look_ahead + 1]:
                delta_1 = np.absolute(value - cur) if abs_delta else value - cur
                if delta_1 > threshold:
                    mask[i + 1] = False
                    i += 1
                else:
                    break
        i += 1
    return mask


###############################################################################


def filter_jumps(
    arr,
    threshold,
    look_ahead,
    abs_delta=False,
    vmiss=np.nan,
    remove_repeated=False,
    interpol_jumps=False,
    interpol_kind="linear",
):
    """
    Wrap mask_jumps().

    (!) interpolation assumes equidistant spacing of the independent variable on
      which arr depends.
    """
    if not isinstance(arr, np.ndarray):
        raise ValueError("input array must be of class numpy ndarray.")
    if arr.ndim > 1:
        raise ValueError("input array must be numpy 1d array.")
    if not isinstance(look_ahead, int):
        raise ValueError("parameter look_ahead must be an integer.")
    if look_ahead >= arr.shape[0] or look_ahead < 1:
        raise ValueError(f"parameter look_ahead must be >=1 and <{arr.shape[0]}.")

    result = arr.copy()  # do not touch the input...
    if not np.isnan(vmiss):
        result[vmiss] = np.nan
    if remove_repeated:
        result[~mask_repeated(result)] = np.nan
    mask = mask_jumps(result, threshold, look_ahead, abs_delta=abs_delta)
    result[~mask] = np.nan
    if interpol_jumps:
        f_ip = interp1d(
            np.arange(0, result.shape[0])[mask],
            result[mask],
            kind=interpol_kind,
            fill_value="extrapolate",
        )
        result = f_ip(np.arange(0, result.shape[0]))
        return (result, mask)
    return (result, mask)


###############################################################################


def filter_jumps_np(
    v,
    max_delta,
    no_val=np.nan,
    use_abs_delta=True,
    reset_buffer_after=3,
    remove_doubles=False,
    interpol_jumps=False,
    interpol_kind="linear",
):
    """
    Mask jumps using numpy functions.

    If v is dependent on another variable x (e.g. time) and if that x
    is not equidistant, do NOT use interpolation.

    Parameters
    ----------
    v : np 1d array
        data to filter.
    max_delta : float
        defines "jump".
    no_val : float, optional
        missing value placeholder. The default is np.nan.
    use_abs_delta : boolean, optional
        use the absolute delta to identify jumps. The default is True.
    reset_buffer_after : int, optional
        how many elements to wait until reset. The default is 3.
    remove_doubles : boolean, optional
        remove elements that are repeated once. The default is False.
    interpol_jumps : boolean, optional
        decide to interpolate filtered values. The default is False.
    interpol_kind : string, optional
        how to interpolate, see scipy.interpolate.interp1d.
        The default is 'linear'.

    Returns
    -------
    dict. 'filtered': filtered data
            'ix_del': indices of deleted elements
            'ix_rem': indices of remaining elements

    """
    ix_del = np.full(v.shape[0], -1, dtype=int)  # deletion index
    ix_rem = np.full(v.shape[0], -1, dtype=int)  # remaining index

    buffer = [False, 0]

    for ix, v_ix in enumerate(v):
        if any([~np.isfinite(v_ix), v_ix == no_val, np.isnan(v_ix)]):
            ix_rem[ix] = ix
            continue  # skip line if value is np.nan

        if not buffer[0]:
            buffer[0] = v_ix
            ix_rem[ix] = ix
            continue  # fill buffer if not done so yet

        delta = abs(v_ix - buffer[0]) if use_abs_delta else v_ix - buffer[0]

        if delta > max_delta:  # jump found!
            v[ix] = no_val
            ix_del[ix] = ix
            buffer[1] += 1
            if reset_buffer_after:
                if buffer[1] == reset_buffer_after:
                    buffer = [v_ix, 0]
        else:  # no jump,...
            buffer[0] = v_ix
            if remove_doubles:  # check for double values...
                if np.isclose(delta, 0.0):  # double found!
                    v[ix] = no_val
                    ix_del[ix] = ix
                else:  # no double
                    ix_rem[ix] = ix
            else:
                ix_rem[ix] = ix

    w_valid = np.where(ix_del != -1)
    ix_del = ix_del[w_valid]

    w_valid = np.where(ix_rem != -1)
    ix_rem = ix_rem[w_valid]

    if interpol_jumps:
        tmp_x = (np.arange(0, v.shape[0]))[ix_rem]
        tmp_y = v[ix_rem]
        f_ip = interp1d(tmp_x, tmp_y, kind=interpol_kind, fill_value="extrapolate")
        filtered = f_ip(np.arange(0, v.shape[0]))
    else:
        w_valid = np.where(v != no_val)
        filtered = v[w_valid]

    return {"filtered": filtered, "ix_del": ix_del, "ix_rem": ix_rem}


###############################################################################


def del_at_edge(v, n_cut, add=2, out_len="same"):
    """
    Extend blocks of NaN elements in an array.

    Assume v to be a 1D array which contains blocks of NaNs.

    Returns: v with "more NaNs", i.e. range of NaN-blocks is extended by n_cut.
    """
    tf = np.isfinite(v) * 1.0

    mask = np.convolve(
        tf, np.ones((int(n_cut + add),)) / int(n_cut + add), mode=out_len
    )

    if tf[0] > 0.9:
        mask[0] = 1.0
    if tf[-1] > 0.9:
        mask[-1] = 1.0

    mask[np.where(mask < 0.999)] = np.nan

    return v * mask


###############################################################################
