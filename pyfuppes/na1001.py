# -*- coding: utf-8 -*-
"""NASA Ames FFI 1001 text file format reader / writer."""

import numpy as np

from .na1001_backend import nasa_ames_1001_rw as rw
from .na1001_backend import nasa_ames_1001_tools as tools

###############################################################################


# initialize class instance with some parameters:
_defaults = {
    "NLHEAD": 14,
    "ONAME": "",
    "ORG": "",
    "SNAME": "",
    "MNAME": "",
    "IVOL": 1,
    "NVOL": 1,
    "DATE": (1970, 1, 1),
    "RDATE": (1970, 1, 1),
    "DX": 0,
    "XNAME": "",
    "NV": 0,
    "VSCAL": 1.0,
    "VMISS": -9999,
    "_VNAME": "",
    "NSCOML": 0,
    "_SCOM": "",
    "NNCOML": 0,
    "_NCOM": "",
    "_X": "",
    "V": "",
    "_FFI": 1001,
    "SRC": "",
    "HEADER": "",
}

_show = (
    "_FFI",
    "SRC",
    "NLHEAD",
    "ONAME",
    "ORG",
    "SNAME",
    "MNAME",
    "IVOL",
    "NVOL",
    "DATE",
    "RDATE",
    "DX",
    "XNAME",
    "NV",
    "VSCAL",
    "VMISS",
    "_VNAME",
    "NSCOML",
    "_SCOM",
    "NNCOML",
    "_NCOM",
)


###############################################################################


class FFI1001(object):
    r"""
    A class to work with NASA Ames files with format index 1001.

    Parameters
    ----------
    file : str or pathlib.Path or file-like
        data source.
    sep : str, optional
        General delimiter. The default is " ".
    sep_data : str, optional
        Delimiter used exclusively in data block. The default is "\t".
    strip_lines : bool, optional
        Remove surrounding whitespaces from all lines before parsing.
        The default is True.
    auto_nncoml : bool, optional
        Automatically determine number of lines in comment blocks.
        The default is True.
    rmv_repeated_seps : bool, optional
        Remove repeated delimiters (e.g. double space). The default is False.
    vscale_vmiss_vertical : bool, optional
        VSCALE and VMISS parameters are arranged vertically over multiple
        lines (1 entry per line) instead of in one line each.
        The default is False.
    vmiss_to_None : bool, optional
        Set True if missing values should be replaced with None. The default is False.
    ensure_ascii : bool, optional
        Enforce ASCII-decoding of the input. The default is True.
    allow_emtpy_data : bool, optional
        Allow header-only input. The default is False.

    Returns
    -------
    FFI 1001 class instance.
    """

    __KEYS = list(_defaults.keys())

    def __init__(self, file=None, **kwargs):
        for k, v in _defaults.items():  # self.__INID.items():
            setattr(self, k, v)
        if file is not None:
            self.__from_file(file, **kwargs)

    def __repr__(self):
        s = "NASA Ames 1001\n---\n"
        s += "".join([f"{k.strip('_')} : {self.__dict__[k]}\n" for k in _show])
        return s

    def __str__(self):
        s = "NASA Ames 1001\n"
        s += f"SRC: {self.SRC}\n---\n"
        s += "\n".join(f"{k}: {getattr(self, k)}" for k in self.__KEYS[1:4])
        s += "\n" + ", ".join(f"{k}: {getattr(self, k)}" for k in self.__KEYS[7:9])
        return s

    @property
    def SCOM(self):
        """Special comments block"""
        return self._SCOM

    @SCOM.setter
    def SCOM(self, value):
        self._SCOM, self.NSCOML = value, len(value)
        self.NLHEAD = 14 + self.NSCOML + self.NNCOML + self.NV

    @property
    def NCOM(self):
        """Normal comments block"""
        return self._NCOM

    @NCOM.setter
    def NCOM(self, value):
        self._NCOM, self.NNCOML = value, len(value)
        self.NLHEAD = 14 + self.NSCOML + self.NNCOML + self.NV

    @property
    def VNAME(self):
        """Variables name block"""
        return self._VNAME

    @VNAME.setter
    def VNAME(self, value):
        self._VNAME, self.NV = value, len(value)
        self.NLHEAD = 14 + self.NSCOML + self.NNCOML

    @property
    def X(self):
        """Independent variable"""
        return self._X

    @X.setter
    def X(self, xarr):
        self._X = xarr
        # calculate dx as unique diffs in X,
        # unique with floats might fail, so add a round to 4 decimals:
        dx = np.unique(np.diff(np.array(xarr, dtype=float)).round(4))
        # let dx be 0 if there's more than one unique diff
        dx = dx[0] if dx.size == 1 else 0
        # use an integer if dx is close to its integer value, else float:
        dx = int(dx) if np.isclose(dx, int(dx)) else dx
        self.DX = dx

    # ------------------------------------------------------------------------------
    def __from_file(self, file, **kwargs):
        """Load NASA Ames 1001 from text file."""
        nadict = rw.na1001_cls_read(file, **kwargs)
        for k in self.__KEYS:
            setattr(self, k, nadict[k])

    # ------------------------------------------------------------------------------
    def to_file(self, file, **kwargs):
        """
        Write NASA Ames 1001 file from populated ffi_1001 class.

        Parameters
        ----------
        file : str or pathlib.Path
            filepath and -name of the destination.
        sep : str, optional
            General delimiter. The default is " ".
        sep_data : str, optional
            Delimiter to separate data columns. The default is "\t".
        overwrite : int, optional
            Set to 1 to overwrite existing files. The default is 0 (no overwrite).
        verbose : bool, optional
            Verbose print output if True. The default is False.

        Returns
        -------
        int
            0 -> failed, 1 -> successful write, 2 -> successful overwrite.

        """
        io = rw.na1001_cls_write(file, self.__dict__, **kwargs)
        return io

    # ------------------------------------------------------------------------------
    def to_dict_nparray(self, **kwargs):
        """
        Make dictionary of numpy 1D arrays from ffi_1001 class instance.

        Parameters
        ----------
        selVnames : list of string, optional
            VNAMEs to be converted. The default is None.
        return_pddf : bool, optional
            Set to True to make the function return a Pandas dataframe.
            The default is False.
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
        dict
            dictionary holding numpy arrays for variables from the na1001 class
            instance.

        """
        return tools.naDict_2_npndarr(self.__dict__, **kwargs)

    # ------------------------------------------------------------------------------
    def to_pddf(self, **kwargs):
        """
        Make a pandas DataFrame from NA 1001 data (X and V).

        Parameters
        ----------
        sep_colhdr : str, optional
            separator used in column header (last line of NCOM). Default is tab.
        idx_colhdr : int, optional
            look for column header in NCOM at index idx_colhdr. Default is -1.
        dtype : numpy array data type, optional
            data type to use for conversion to DataFrame. Default is float.
        add_datetime_index: boolean, optional
            add a DateTime index to the df. The default is False.

        Returns
        -------
        pandas.DataFrame
            dataframe with a column for X and one for each parameter in V.

        """
        return tools.naDict_2_pddf(self.__dict__, **kwargs)

    # ------------------------------------------------------------------------------
    def to_poldf(self, **kwargs):
        """
        Make a polars DataFrame from NA 1001 data (X and V).

        Parameters
        ----------
        sep_colhdr : str, optional
            separator used in column header (last line of NCOM). Default is tab.
        idx_colhdr : int, optional
            look for column header in NCOM at index idx_colhdr. Default is -1.
        add_datetime: boolean, optional
            add a DateTime column to the df. The default is False.
        nan_to_none: boolean, optional
            fill NaN values with polars' Null. The default is False.

        Returns
        -------
        polars.DataFrame
            dataframe with a column for X and one for each parameter in V.

        """
        return tools.naDict_2_poldf(self.__dict__, **kwargs)
