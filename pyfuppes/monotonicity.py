# -*- coding: utf-8 -*-
"""Check monotonicity of Python lists and numpy 1D arrays."""

import numpy as np

###############################################################################


### Python list
def strictly_increasing(py_list: list) -> bool:
    """Check if elements of a list are strictly increasing."""
    return all(x < y for x, y in zip(py_list, py_list[1:]))


def strictly_decreasing(py_list: list) -> bool:
    """Check if elements of a list are strictly decreasing."""
    return all(x > y for x, y in zip(py_list, py_list[1:]))


def non_increasing(py_list: list) -> bool:
    """Check if elements of a list are increasing monotonically."""
    return all(x >= y for x, y in zip(py_list, py_list[1:]))


def non_decreasing(py_list: list) -> bool:
    """Check if elements of a list are decreasing monotonically."""
    return all(x <= y for x, y in zip(py_list, py_list[1:]))


### Numpy 1D array
def strict_inc_np(npndarr_1d: np.ndarray) -> np.bool_:
    """Check if elements of numpy 1D array are strictly increasing."""
    return np.all(np.diff(npndarr_1d) > 0)


def strict_dec_np(npndarr_1d: np.ndarray) -> np.bool_:
    """Check if elements of numpy 1D array are strictly decreasing."""
    return np.all(np.diff(npndarr_1d) < 0)


def non_inc_np(npndarr_1d: np.ndarray) -> np.bool_:
    """Check if elements of numpy 1D array are increasing monotonically."""
    return np.all(np.diff(npndarr_1d) <= 0)


def non_dec_np(npndarr_1d: np.ndarray) -> np.bool_:
    """Check if elements of numpy 1D array are decreasing monotonically."""
    return np.all(np.diff(npndarr_1d) >= 0)
