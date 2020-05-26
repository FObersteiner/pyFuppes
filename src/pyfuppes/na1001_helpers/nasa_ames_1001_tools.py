# -*- coding: utf-8 -*-
r"""
Created on Wed May 29 08:35:12 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from pyfuppes.timeconversion import mdns_2_dtobj


###############################################################################


def naDict_2_npndarr(naDict,
                     selVnames=None,
                     splitVname=';', splitIdx=0,
                     xdtype=np.float, vdtype=np.float,
                     vmiss=np.NaN, create_x=True):
    """
    convert variables from a NASA AMES 1001 dictionary stored as string(lists)
    to numpy nd array type.

    Parameters
    ----------
    naDict : NASA AMES 1001 data in Python dict.
        ...as returned by nasa_ames_1001_read.
    selVnames : list of string, optional
        VNAMEs to be converted. The default is None.
    splitVname : string, optional
        Where to split entries in VNAME. The default is ';'.
    splitIdx : int, optional
        Which part of split result to use, see splitVname. The default is 0.
    xdtype : data type, optional
        Data type for independent variable X. The default is np.float.
    vdtype : data type, optional
        Data type for dependent variable(s). The default is np.float.
    vmiss : missing value identifier, optional
        The default is np.NaN.

    Returns
    -------
    npDict : dict
        dictionary holding numpy arrays for variables from the NASA AMES file.

    """
    npDict = {naDict['XNAME'][0]: np.array(naDict['X'], dtype=xdtype)}

    # convenience: link npDict['x'] to npDict[naDict['XNAME'][0]]
    if create_x:
        npDict['x'] = npDict[naDict['XNAME'][0]]

    if not selVnames:
        selVnames = [n.split(splitVname)[0] for n in naDict['VNAME']]

    # for each parameter, find its index in naDict['V']
    for parm in selVnames:
        if splitVname:
            ix = [l.split(splitVname)[splitIdx] for l in naDict['VNAME']].index(parm)
        else:
            ix = naDict['VNAME'].index(parm)
        npDict[parm] = np.array(naDict['V'][ix], dtype=vdtype)

        # check vmiss: make sure that vmiss=0 also works by checking for type
        # boolean. Might be a bit confusing since vmiss=True would also result
        # in keeping the original values.
        if not isinstance(vmiss, bool):
            npDict[parm][np.isclose(npDict[parm], float(naDict['VMISS'][ix]))] = vmiss
        # account for VSCAL:
        npDict[parm] *= float(naDict['VSCAL'][ix])

    return npDict


###############################################################################


def naDict_2_pddf(naDict,
                  sep_colhdr='\t', idx_colhdr=-1,
                  dtype=np.float64,
                  add_datetime_index=False):
    """
    WHAT?
        wrapper for nasa_ames_1001_read() that just returns a Pandas DataFrame
    ASSUMES:
        last line of NCOM contains names of parameters (delimited by sep_data)

    Parameters
    ----------
    sep_colhdr : str, optional
        separator used in column header (last line of NCOM). Default is tab.
    idx_colhdr : int, optional
        look for column header in NCOM at index idx_colhdr. Default is -1.
    dtype : numpy array data type, optional
        data type to use for conversion to DataFrame. Default is np.float64.
    add_datetime_index: boolean, optional
        add a DateTime index to the df. The default is False.

    Returns
    -------
    Pandas DataFrame
        dataframe with a column for X and one for each parameter in V.

    """
    # column names for the DataFrame:
    keys = naDict['NCOM'][idx_colhdr].split(sep_colhdr)

    # begin extraction with independent variable:
    values = [np.array(naDict['X'], dtype=dtype)]

    # include scaling factors and missing values:
    vmiss = [float(s) for s in naDict['VMISS']]
    vscal = [float(s) for s in naDict['VSCAL']]

    # for each variable...
    for i, v_n in enumerate(naDict['V']):
        # cast list of string to np.array:
        arr = np.array(v_n, dtype=dtype)
        # replace missing values with np.nan:
        arr[np.isclose(arr, vmiss[i])] = np.nan
        # add array to list of arrays:
        values.append(arr*vscal[i])

    df = pd.DataFrame.from_dict(dict(zip(keys, values)))

    if add_datetime_index:
        i = pd.DatetimeIndex(mdns_2_dtobj(values[0], ref_date=naDict['DATE']))
        df = df.set_index(i)

    return df

