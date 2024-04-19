# -*- coding: utf-8 -*-
"""NASA Ames FFI 1001 text file format reader / writer."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
import polars as pl

from .na1001_backend import nasa_ames_1001_rw as rw
from .na1001_backend import nasa_ames_1001_tools as tools

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

    def __init__(self, file=None, **kwargs):
        today = datetime.now(timezone.utc).date()
        self.NLHEAD = 14  # minimum number of header lines is 14
        self.ONAME = "data origin"
        self.ORG = "organization"
        self.SNAME = "sampling description"
        self.MNAME = "mission name"
        self.IVOL = 1
        self.NVOL = 1
        self.DATE = (1970, 1, 1)
        self.RDATE = (today.year, today.month, today.day)
        self.DX = 0
        self.XNAME = "x name"
        self.NV = 1
        self.VSCAL = ["1"]
        self.VMISS = ["-9999"]
        self._VNAME = ["v names"]
        self.NSCOML = 0
        self._SCOM = ["special comments"]
        self.NNCOML = 0
        self._NCOM = ["normal comments"]
        self._X = [""]
        self.V = [[""]]
        self._SRC = "path to file"
        self._HEADER = "file header"

        if file is not None:
            self.__from_file(file, **kwargs)

    @property
    def FFI(self):
        """FFI is always 1001, as the class name indicates..."""
        return 1001

    @property
    def SCOM(self) -> list[str]:
        """Special comments block"""
        return self._SCOM

    @SCOM.setter
    def SCOM(self, value: list[str]):
        self._SCOM, self.NSCOML = value, len(value)
        self.NLHEAD = 14 + self.NSCOML + self.NNCOML + self.NV

    @property
    def NCOM(self) -> list[str]:
        """Normal comments block"""
        return self._NCOM

    @NCOM.setter
    def NCOM(self, value: list[str]):
        self._NCOM, self.NNCOML = value, len(value)
        self.NLHEAD = 14 + self.NSCOML + self.NNCOML + self.NV

    @property
    def VNAME(self) -> list[str]:
        """Variables name block"""
        return self._VNAME

    @VNAME.setter
    def VNAME(self, value: list[str]):
        self._VNAME, self.NV = value, len(value)
        self.NLHEAD = 14 + self.NSCOML + self.NNCOML

    @property
    def X(self) -> list[str]:
        """Independent variable"""
        return self._X

    @X.setter
    def X(self, xarr: list[str]):
        self._X = xarr
        # calculate dx as unique diffs in X,
        # unique with floats might fail, so add a round to 4 decimals:
        dx = np.unique(np.diff(np.array(xarr, dtype=float)).round(4))
        # let dx be 0 if there's more than one unique diff
        dx = dx[0] if dx.size == 1 else 0
        # use an integer if dx is close to its integer value, else float:
        dx = int(dx) if np.isclose(dx, int(dx)) else dx
        self.DX = dx

    @property
    def V(self) -> list[list[str],]:
        """Dependent variable"""
        return self._V

    @V.setter
    def V(self, vlists: list[list[str],]):
        # assert (
        #     len(vlists) == self.NV
        # ), f"try to set {len(vlists)} dependent variables, but VNAMES specify {self.NV}"
        self._V = vlists

    # ------------------------------------------------------------------------------
    def __from_file(self, file: Union[str, Path], **kwargs):
        """Load NASA Ames 1001 from text file."""
        nadict = rw.na1001_cls_read(file, **kwargs)
        for k in rw.KEYS:
            setattr(self, k, nadict[k])

    # ------------------------------------------------------------------------------
    def to_file(self, file: Union[str, Path], **kwargs):
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
    def to_dict_nparray(self, **kwargs) -> dict[str, np.ndarray]:
        """
        Make dictionary of numpy 1D arrays from FFI1001 class instance.

        Parameters
        ----------
        sel_vnames : list of string, optional
            VNAMEs to be converted. The default is None.
        clean_vnames : boolean, optional
            remove whitespaces from variable names. The default is False.
        vname_delimiter : string, optional
            Where to split entries in VNAME. The default is ';'.
        split_idx : int, optional
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
    def to_pddf(self, **kwargs) -> pd.DataFrame:
        """
        Make a pandas DataFrame from NA 1001 data (X and V).

        Parameters
        ----------
        sep_colhdr : str, optional
            separator used in column header (last line of NCOM). Default is tab.
        idx_colhdr : int, optional
            look for column header in NCOM at index idx_colhdr. Default is -1.
        clean_colnames : boolean, optional
            remove whitespaces from variable names. The default is False.
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
    def to_poldf(self, **kwargs) -> pl.DataFrame:
        """
        Make a polars DataFrame from NA 1001 data (X and V).

        Parameters
        ----------
        sep_colhdr : str, optional
            separator used in column header (last line of NCOM). Default is tab.
        idx_colhdr : int, optional
            look for column header in NCOM at index idx_colhdr. Default is -1.
        clean_colnames : boolean, optional
            remove whitespaces from variable names. The default is False.
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

    # ------------------------------------------------------------------------------
    def __repr__(self) -> str:
        s = f"NASA Ames {self.FFI}\n---\n"
        s += "".join(
            [
                f"{k.strip('_')} : {self.__dict__[k]}\n"
                for k in (
                    "_SRC",
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
            ]
        )
        return s

    def __str__(self) -> str:
        s = "NASA Ames 1001\n"
        s += f"SRC: {self._SRC}\n---\n"
        s += "\n".join(f"{k}: {getattr(self, k)}" for k in ["ONAME", "ORG", "SNAME"])
        s += "\n" + ", ".join(f"{k}: {getattr(self, k)}" for k in ["DATE", "RDATE"])
        return s
