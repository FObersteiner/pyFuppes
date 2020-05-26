# -*- coding: utf-8 -*-
r"""
Created on Wed Feb 21 17:49:25 2018

@author: F. Obersteiner, florian\obersteiner\\kit\edu

Info:
    some useful functions to handle CARIBIC data, i.e. CARIBIC-specific
    file names, paths on the server etc.
"""

import os
import re
from datetime import datetime
from pathlib import Path


###############################################################################


def NAfilename_to_Flight_No(file_name, length=3):
    """
    input file_name "type_date_flight_from_to_version.txt"
    string separator is _ (underscore)
    flight no is found after the second occurance of string separator
    flight no has 3 digits by default ("length" keyword)
    """
    file_name = os.path.basename(file_name) # remove path if supplied
    substring = file_name[file_name.find("_")+1:]
    return int(substring[substring.find("_")+1:substring.find("_")+1+length])


###############################################################################


def NAfilename_to_dtObj(name, pos=1, fmt="%Y%m%d", sep="_"):
    """
    file_name: "type_date_flight_from_to_version.txt",
        string separator is _ (underscore)
    pos: position in splitted filename where to look for date
    fmt: format, "%Y%m%d" by default
    """
    namel = os.path.basename(name).rsplit(sep)
    if fmt == "%Y%m%d":
        return datetime(int(namel[pos][:4]), int(namel[pos][4:6]),
                         int(namel[pos][6:]))
    return datetime.strptime(namel[pos], fmt)


###############################################################################


def Flight_No_to_Flight_Dir(flight_no, *,
                            flights_dir="//IMK-ASF-CARFS1/Caribic/extern/Caribic2data/Flights"):
    """
    search flights folder on Caribic server for folder with specified flight_no.
    returns None if no suited flight folder is found.
    """
    flights_dir = Path(flights_dir)
    for f in os.listdir(flights_dir):
        if f.startswith(f"Flight{flight_no:03d}_"):
            return flights_dir / f


###############################################################################


def Flight_No_to_ModelData_Dir(flight_no, *,
                               model_dir="//IMK-ASF-CARFS1/Caribic/extern/Caribic2data/data_model"):
    """
    search model data folder on Caribic server for folder with specified flight_no.
    returns None of no suited model data folder is found.
    """
    model_dir = Path(model_dir)
    for f in os.listdir(model_dir):
        if f.endswith(f"_{flight_no:03d}"):
            return model_dir / f


###############################################################################


def Find_NAfile(flight_no, prfx, *,
                flights_dir="//IMK-ASF-CARFS1/Caribic/extern/Caribic2data/Flights",
                file_dir="",
                binned_10s=False,
                newest_only=True,
                show_error=False):
    """
    find NASA AMES file in flights directory (CARIBIC server folder structure).

    Parameters
    ----------
    flight_no : str representing an int or int
        flight number.
    prfx : str
        file name prefix specifying the data origin, e.g. 'MA' for master data.
    flights_dir : str, optional
        directory with subdirectories containing flight data.
        The default is "//IMK-ASF-CARFS1/Caribic/extern/Caribic2data/Flights".
    file_dir : str, optional
        specific folder where to look for NASA AMES file(s). The default is "".
    binned_10s : bool, optional
        set to True to return files with the '10s' version prefix, specifying
        data binned to 10s intervals. The default is False.
    newest_only: bool, optional
        if there are multiple files of a certain origin (e.g. V01 and V02),
        only the file with the highest version suffix is returned.

    Returns
    -------
    files : Path object
        ...or None if nothing is found.

    """
    flight_no = int(flight_no)

    flights_dir = Path(flights_dir)
    if file_dir:
        file_dir = Path(file_dir)
    else:
        file_dir = Flight_No_to_Flight_Dir(flight_no, flights_dir=flights_dir)

    pattern = f"{prfx}_[0-9]{{8}}_{flight_no:03d}_[A-Z]{{3}}_[A-Z]{{3}}_V[0-9]{{2}}.txt"
    if binned_10s:
        pattern = f"{prfx}_[0-9]{{8}}_{flight_no:03d}_[A-Z]{{3}}_[A-Z]{{3}}_10s_V[0-9]{{2}}.txt"

    files = [file_dir/f for f in os.listdir(file_dir) if re.match(pattern, f)]

    if not files and show_error:
        raise FileNotFoundError(f"nothing found for re pattern {pattern}")

    if newest_only and len(files) > 1:
        return sorted(files)[-1]

    return files[0] if files else None



###############################################################################


def NAfile_get_vers_num(file, sep="_"):
    """
    find version number in file (can be path with filename or only filename).
    assumes filename of type "Vxx.ext" with xx=version and ext=file extension.
    parts of the filename are expected to be separated from each other by "sep".
    """
    if not isinstance(file, str):
        file = str(file) # might be a path object

    ix_ext, ix_vsep = file.rfind("."), file.rfind(sep)

    if ix_ext != -1 and ix_vsep != -1:
        vers_str = ((file[ix_vsep:ix_ext]).upper())[2:]
        try:
            vers_num = int(vers_str)
        except ValueError:
            vers_num = None # conversion to integer failed
        return vers_num
    return None # neither . nor _ found in filename


###############################################################################


def NAfilename_inc_vers(file, sep="_", add_suffix="", add_prefix="",
                        def_versnum=False, increment_by=1):
    """
    increment the version number specified in the file name
    of a Caribic Nasa Ames formatted text file.
    parts of the filename are expected to be separated from each other by "sep".
    """
    if not isinstance(file, str):
        file = str(file) # might be a path object

    ix_ext, ix_vsep = file.rfind("."), file.rfind(sep)

    if ix_ext != -1:
        file_ext = file[ix_ext:]
        if ix_ext != -1 and ix_vsep != -1:
            vers_str = ((file[ix_vsep:ix_ext]).upper())[2:]
            try:
                vers_num = int(vers_str)
            except ValueError:
                vers_num = -1 # conversion to integer failed
        else:
            vers_num = -1 # neither . nor _ found in filename

        if vers_num != -1:
            if def_versnum:
                vers_num = def_versnum
            else:
                vers_num += increment_by

            vers_str = "_V" + str('%2.2u' % vers_num)
            if len(add_suffix) > 0 or len(add_prefix) > 0:
                file_inc_v = file[:ix_vsep]+add_prefix+vers_str+add_suffix+file_ext
            else:
                file_inc_v = file[:ix_vsep]+vers_str+file_ext

        return Path(file_inc_v)
    return None


###############################################################################


def NAfilename_new_version_tag(file, v_data=1, v_file=1, sep="_"):
    """
    replace the old version tag Vxx with Vxx.yy with
        xx = data version, integer, 0-99
        yy = file version, integer, 0-99
    ...and e.g. version 1 written as "01" etc.
    file: string, full path or only filename
    v_data and v_file: versions in output
    sep: separator, e.g. file = "*_Vxx.yy.txt" -> sep is "_"
    """
    if not isinstance(file, str):
        file = str(file) # might be a path object

    ix_ext = file.rfind(".") # find file extension

    if ix_ext != -1:
        vers_new = "_V"+str('%2.2u' % v_data)+"."+str('%2.2u' % v_file)
        ix_sep = file.rfind(sep) # find separator between version and rest of name
        file_new_vtag = file[:ix_sep]+vers_new+file[ix_ext:]

        return file_new_vtag
    return None


###############################################################################


def NAfile_get_vers_newtag(file, sep_v=".", sep="_"):
    """
    retrieve data- and file version from version tag "*_Vxx.yy"
    """
    if not isinstance(file, str):
        file = str(file) # might be a path object but must be str for .rfind()

    ix_ext = file.rfind(".") # file extension

    if ix_ext != -1:
        ix_vsep = (file[0:ix_ext]).rfind(sep_v) # sep: data- and file version
        ix_sep = (file[0:ix_vsep]).rfind(sep) # sep: version tag and rest of filename
        version = {'v_data': int(file[ix_sep+2:ix_vsep]),
                   'v_file': int(file[ix_vsep+1:ix_ext])}

        return version
    return None


###############################################################################
