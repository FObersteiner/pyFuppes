# -*- coding: utf-8 -*-
"""NA helpers."""

from datetime import datetime

import numpy as np
import pandas as pd
import polars as pl

###############################################################################

MICROSECONDS_PER_SECOND = 1_000_000

###############################################################################


def naDict_2_npndarr(
    naDict,
    sel_vnames=None,
    clean_vnames=False,
    vname_delimiter=";",
    split_idx=0,
    xdtype=float,
    vdtype=float,
    vmiss=np.NaN,
):
    """
    Convert variables from na1001 class instance to dictionary mapping names to numpy arrays.

    See class method for detailed doc-string.
    """
    npDict = {naDict["XNAME"].split(vname_delimiter)[0]: np.array(naDict["_X"], dtype=xdtype)}

    if not sel_vnames:
        sel_vnames = [n.split(vname_delimiter)[0] for n in naDict["_VNAME"]]

    if clean_vnames:
        sel_vnames = [k.replace(" ", "") for k in sel_vnames]

    # for each parameter, find its index in naDict['V']
    for parm in sel_vnames:
        if vname_delimiter:
            ix = [name.split(vname_delimiter)[split_idx] for name in naDict["_VNAME"]].index(parm)
        else:
            ix = naDict["_VNAME"].index(parm)
        npDict[parm] = np.array(naDict["_V"][ix], dtype=vdtype)

        # check vmiss: make sure that vmiss=0 also works by checking for type
        # boolean. Might be a bit confusing since vmiss=True would also result
        # in keeping the original values.
        if not isinstance(vmiss, bool):
            npDict[parm][np.isclose(npDict[parm], float(naDict["VMISS"][ix]))] = vmiss
        # account for VSCAL:
        npDict[parm] *= float(naDict["VSCAL"][ix])

    return npDict


###############################################################################


def naDict_2_pddf(
    naDict,
    sep_colhdr="\t",
    idx_colhdr=-1,
    clean_colnames=False,
    dtype=float,
    add_datetime_index=False,
):
    """
    Convert variables from na1001 class instance to pandas dataframe.

    See class method for detailed doc-string.
    """
    # column names for the DataFrame. NA reader does not give us column names,
    # so we need to handle them here.
    keys = naDict["_NCOM"][idx_colhdr].split(sep_colhdr)
    if clean_colnames:
        keys = [k.replace(" ", "") for k in keys]

    # begin extraction with independent variable:
    values = [np.array(naDict["_X"], dtype=dtype)]

    # include scaling factors and missing values:
    vmiss = [float(s) for s in naDict["VMISS"]]
    vscal = [float(s) for s in naDict["VSCAL"]]

    # for each variable...
    for i, v_n in enumerate(naDict["_V"]):
        # cast list of string to np.array:
        arr = np.array(v_n, dtype=dtype)
        # replace missing values with np.nan:
        arr[np.isclose(arr, vmiss[i])] = np.nan
        # add array to list of arrays:
        values.append(arr * vscal[i])

    df = pd.DataFrame.from_dict(dict(zip(keys, values)))

    if add_datetime_index:
        df.set_index(
            pd.DatetimeIndex(
                pd.Timestamp(*naDict["DATE"]) + pd.to_timedelta(values[0], unit="s"),
                tz="UTC",
            ),
            inplace=True,
        )

    return df


###############################################################################


def naDict_2_poldf(
    naDict,
    sep_colhdr="\t",
    idx_colhdr=-1,
    clean_colnames=False,
    add_datetime=False,
    nan_to_none=False,
    _dtype=float,
):
    """
    Convert variables from na1001 class instance to polars dataframe.

    See class method for detailed doc-string.
    """
    # column names for the DataFrame. NA reader does not give us column names,
    # so we need to handle them here.
    keys = naDict["_NCOM"][idx_colhdr].split(sep_colhdr)
    if clean_colnames:
        keys = [k.replace(" ", "") for k in keys]

    # # begin extraction with independent variable:
    values = [np.array(naDict["_X"], dtype=_dtype)]

    # # include scaling factors and missing values:
    vmiss = [float(s) for s in naDict["VMISS"]]
    vscal = [float(s) for s in naDict["VSCAL"]]

    # for each variable...
    for i, v_n in enumerate(naDict["_V"]):
        # cast list of string to np.array:
        arr = np.array(v_n, dtype=_dtype)
        # replace missing values with np.nan:
        arr[np.isclose(arr, vmiss[i])] = np.nan
        # add array to list of arrays:
        values.append(arr * vscal[i])

    df = pl.DataFrame(dict(zip(keys, values)))

    if add_datetime:
        df = df.with_columns(
            (
                datetime(*naDict["DATE"])  # this will give µs resolution by default
                + pl.duration(microseconds=pl.col(keys[0]) * MICROSECONDS_PER_SECOND)
            ).alias("datetime")
        )

    if nan_to_none:
        return df.fill_nan(None)

    return df
