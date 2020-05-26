# -*- coding: utf-8 -*-
"""
Created on Fri May 22 16:16:00 2020

@author: F. Obersteiner, f/obersteiner//kit/edu
"""

from pyfuppes.na1001_helpers.nasa_ames_1001_rw import nasa_ames_1001_read
from pyfuppes.na1001_helpers.nasa_ames_1001_rw import nasa_ames_1001_write
from pyfuppes.na1001_helpers.nasa_ames_1001_tools import naDict_2_npndarr
from pyfuppes.na1001_helpers.nasa_ames_1001_tools import naDict_2_pddf


###############################################################################


### TODO
# automatically determine number of lines in header, ncom, scom etc.
class na1001():
    """
    a class to work with NASA AMES files of type 1001.
    """
    # file format identifier is always 1001, so make it a class attribute:
    FFI = 1001
    # sourc
    SRC = None
    # keys are also always the same for the class:
    KEYS = ('NLHEAD', 'ONAME', 'ORG', 'SNAME', 'MNAME', 'IVOL', 'NVOL',
            'DATE', 'RDATE', 'DX', 'XNAME', 'NV', 'VSCAL', 'VMISS', 'VNAME',
            'NSCOML', 'SCOM', 'NNCOML', 'NCOM', 'X', 'V')

    # if no filename is supplied, initialize all attributes to None
    def __init__(self, fromfile=None, **kwargs):
        for k in self.KEYS:
            setattr(self, k, None)
        if fromfile is not None:
            self.from_file(fromfile, **kwargs)
            self.SRC = str(fromfile)

    def __repr__(self):
        s = "NASA AMES 1001\n"
        s += f"SRC: {self.SRC}\n---\n"
        s += '\n'.join(f"{k}: {getattr(self, k)}" for k in self.KEYS[3:4])
        s += '\n' + ', '.join(f"{k}: {getattr(self, k)}" for k in self.KEYS[7:9])
        s += f'\nXNAME: {self.XNAME}'
        sv = "\n".join(v for v in self.VNAME)
        s += f'\nNV: {self.NV}, VNAMES:\n{sv}'
        return s

    def __str__(self):
        s = "NASA AMES 1001\n"
        s += f"SRC: {self.SRC}\n---\n"
        s += '\n'.join(f"{k}: {getattr(self, k)}" for k in self.KEYS[1:4])
        s += '\n' + ', '.join(f"{k}: {getattr(self, k)}" for k in self.KEYS[7:9])
        return s

#------------------------------------------------------------------------------
    def from_file(self, file, **kwargs):
        """
        Load NASA AMES 1001 from file.

        Parameters
        ----------
        file : path to file
        **kwargs :
            sep=" ": general string separator
            sep_com=";": separator used exclusively in comment block
            sep_data="\t": separator used exclusively in data block
            auto_nncoml=True: automatically determine number of lines in normal comment blocks
            strip_lines=True: remove whitespaces from all file lines
            remove_doubleseps=False: remove repeated occurrences of general separator
            vscale_vmiss_vertical=False: set to True if VSCALE and VMISS parameters
                                         are arranged vertically over multiple
                                         lines (1 entry per line) instead of in one
                                         line each (e.g. for DLR Bahamas files)
            vmiss_to_None: set True if missing values should be replaced with None.
            ensure_ascii: check if all bytes in the specified file are < 128.
        """
        nadict = nasa_ames_1001_read(file, **kwargs)
        for k in self.KEYS:
            setattr(self, k, nadict[k])

#------------------------------------------------------------------------------
    def to_file(self, file, **kwargs):
        """
        Write NASA AMES 1001 file from class attributes.

        Parameters
        ----------
        file : filename of output file.

        **kwargs
        ----------
        sep - separator (general)
        sep_com - separator used in comment section
        sep_data - separator used in data section
        crlf - newline character(s)
        overwrite - set to True to overwrite if file exists
        verbose - print info to the console
        """
        io = nasa_ames_1001_write(file, self.__dict__, **kwargs)
        return io

#------------------------------------------------------------------------------
    def to_dict_nparray(self, **kwargs):
        """
        convert variables from a NASA AMES 1001 dictionary stored as string(lists)
        to numpy nd array type.

        Parameters
        ----------
        None.

        **kwargs
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
        npDict : dict
            dictionary holding numpy arrays for variables from the NASA AMES file.

        """
        return naDict_2_npndarr(self.__dict__, **kwargs)

#------------------------------------------------------------------------------
    def to_pddf(self, **kwargs):
        """
        make a Pandas DataFrame from NA 1001 data.

        Parameters
        ----------
        None.

        **kwargs
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
        return naDict_2_pddf(self.__dict__, **kwargs)

