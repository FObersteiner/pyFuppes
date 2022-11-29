# -*- coding: utf-8 -*-
"""NA helpers."""

import numpy as np
import pandas as pd


###############################################################################


def naDict_2_npndarr(
    naDict,
    selVnames=None,
    splitVname=";",
    splitIdx=0,
    xdtype=float,
    vdtype=float,
    vmiss=np.NaN,
):
    """
    Convert variables from na1001 class instance to dictionary holding numpy arrays.

    See class method for detailled docstring.
    """
    npDict = {
        naDict["XNAME"].split(splitVname)[0]: np.array(naDict["_X"], dtype=xdtype)
    }

    if not selVnames:
        selVnames = [n.split(splitVname)[0] for n in naDict["_VNAME"]]

    # for each parameter, find its index in naDict['V']
    for parm in selVnames:
        if splitVname:
            ix = [name.split(splitVname)[splitIdx] for name in naDict["_VNAME"]].index(
                parm
            )
        else:
            ix = naDict["_VNAME"].index(parm)
        npDict[parm] = np.array(naDict["V"][ix], dtype=vdtype)

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
    naDict, sep_colhdr="\t", idx_colhdr=-1, dtype=float, add_datetime_index=False
):
    """
    Convert variables from na1001 class instance to pandas dataframe.

    See class method for detailled docstring.
    """
    # column names for the DataFrame:
    keys = naDict["_NCOM"][idx_colhdr].split(sep_colhdr)

    # begin extraction with independent variable:
    values = [np.array(naDict["_X"], dtype=dtype)]

    # include scaling factors and missing values:
    vmiss = [float(s) for s in naDict["VMISS"]]
    vscal = [float(s) for s in naDict["VSCAL"]]

    # for each variable...
    for i, v_n in enumerate(naDict["V"]):
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
