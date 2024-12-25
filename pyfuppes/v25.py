# -*- coding: utf-8 -*-
"""Tools to handle logfiles from the V25 microcontroller's memory card."""

import os
import pathlib
import platform
from datetime import datetime, timezone
from itertools import chain
from typing import Iterator, Optional, Union

import tomli as toml_r

from pyfuppes.misc import insensitive_pattern, to_list_of_Path
from pyfuppes.txt2dict import txt_2_dict

try:
    wd = pathlib.Path(__file__).parent
except NameError:
    wd = pathlib.Path.cwd()  # same as os.getcwd()
assert wd.is_dir(), "faild to obtain working directory"


# CONSTANTS -------------------------------------------------------------------

CLEANUP_DONE = "V25Logs_cleanup.done"
PATH_V25_DATA_CFG = wd / "v25_config/v25_data_cfg.toml"
V25_DATA_SEP = "\t"
V25_DATA_MIN_NLINES = 2


# --- INTERNALS ---------------------------------------------------------------


def _get_sel_files(
    folders: list[pathlib.Path], file_extensions: list[str], insensitive: bool = True
) -> Iterator[pathlib.Path]:
    """
    Make an iterator that yields all files in "folders" having one of the extensions listed in "file_extensions".

    Keyword "insensitive" only has an effect on Unix platforms - on Windows, glob is always case-insensitive.
    """
    assert all(
        (isinstance(i, list) for i in (folders, file_extensions))
    ), "all inputs must be of type list."

    if insensitive and platform.system().lower() != "windows":
        file_extensions = [insensitive_pattern(e) for e in file_extensions]

    sel_files = chain()
    for f in folders:
        for e in file_extensions:
            sel_files = chain(sel_files, f.glob(f"*{e}"))

    return sel_files


def _V25logs_cleaned_dump(path: pathlib.Path):
    """Dump an empty file signaling that this folder of V25 logfiles has been cleaned."""
    with open(path / CLEANUP_DONE, "w", encoding="UTF-8") as _:
        pass


# --- EXTERNALS ---------------------------------------------------------------


def logs_cleanup(
    directories: list,
    cfg_path: pathlib.Path = PATH_V25_DATA_CFG,
    drop_info: bool = True,
    check_info: bool = True,
    add_osc_datetime: bool = True,
    verbose: bool = False,
):
    """
    Delete empty files and remove incomplete lines from V25 logfiles.

    WARNING: this function has side-effects. It modifies files.

    Parameters
    ----------
    directories : list
        where to clean.
    cfg_path : pathlib.Path, optional
        path to config file that specifies V25 log file types
    drop_info : bool, optional
        drop a file saying "this directories was cleaned". The default is True.
    check_info : bool, optional
        check for drop_info file. The default is True.
    add_osc_datetime : bool, optional
        prepend a datetime column to OSC files. The header datetime is repeated. The default is True.
    verbose : true, optional
        some print-outs to the console. The default is False.

    Returns
    -------
    None.
    """
    verboseprint = print if verbose else lambda *a, **k: None

    directories = to_list_of_Path(directories)

    if check_info:
        directories = [f for f in directories if CLEANUP_DONE not in os.listdir(f)]

    if not directories:
        verboseprint("*v25_logcleaner* nothing to clean")
        return

    # load file specifications;
    with open(cfg_path, "rb") as fp:
        cfg = toml_r.load(fp)

    # ...this defines which files are checked
    sel_files = sorted(_get_sel_files(directories, list(cfg.keys())))

    for file in sel_files:
        write = False
        with open(file, "r", encoding="utf-8") as file_obj:
            data = file_obj.readlines()

        # all files must have at least 2 lines: column header and one line of data
        if len(data) <= V25_DATA_MIN_NLINES:
            verboseprint(f"*v25_logcleaner* deleted {file.name} which has insufficient lines")
            file.unlink()
            continue

        # ensure last row has enough columns; determine from first line of data
        #   unless it's an OSC file
        if (t := file.suffix.strip(".").upper()) == "OSC":
            n_cols = cfg[t]["n_cols"]
        else:
            n_cols = len([elem for elem in data[0].strip(" \n").split(V25_DATA_SEP) if elem])

        while len([elem for elem in data[-1].strip(" \n").split(V25_DATA_SEP) if elem]) < n_cols:
            write = True
            data = data[:-1]
            verboseprint(
                f"*v25_logcleaner* deleted last line in {file.name} which has insufficient elements"
            )

        # now check minimum lines per file type
        if (
            len(data) < cfg[file.suffix.strip(".").upper()]["min_n_lines"]
        ):  # empty file or header only
            verboseprint(f"*v25_logcleaner* deleted {file.name} which has insufficient lines")
            file.unlink()
            continue

        # check for ragged lines
        for idx, line in enumerate(data):
            if idx < cfg[t]["min_n_lines"] - 1:  # skip header
                continue
            parts = line.strip(V25_DATA_SEP).split(V25_DATA_SEP)
            if len(parts) != n_cols:
                verboseprint(
                    f"*v25_logcleaner* detected invalid number of fields in {file.name}, line {idx+1}"
                    f" - want {n_cols}, have {len(parts)} (truncated)"
                )
                write = True
                new_line = V25_DATA_SEP.join(parts[:n_cols]) + "\n"
                if line.startswith(V25_DATA_SEP):
                    new_line = V25_DATA_SEP + new_line
                data[idx] = new_line

        # OSC files must get a timestamp column
        if add_osc_datetime and file.suffix.strip(".").upper() == "OSC":
            verboseprint(f"*v25_logcleaner* update OSC file {file.name}")
            write = True
            dtstr = data[0].strip("\n")
            # verify by parsing to datetime:
            _ = datetime.strptime(dtstr, "%d.%m.%y %H:%M:%S.%f")
            # only update the files if this wasn't done before already
            if "DateTime" not in data[4]:
                data[4] = V25_DATA_SEP + "DateTime" + data[4]
                data[5:] = [V25_DATA_SEP + dtstr + line for line in data[5:]]

        if write:
            with open(file, "w", encoding="utf-8") as fp:
                fp.writelines(data)

    verboseprint("*v25_logcleaner* done.")

    if drop_info:
        for d in directories:
            if not list(d.glob(CLEANUP_DONE)):
                _V25logs_cleaned_dump(d)


###############################################################################


def collect_V25Logs(
    folder: Union[str, list[str], pathlib.Path, list[pathlib.Path]],
    ext: Union[str, list[str]],
    delimiter: str = V25_DATA_SEP,
    colhdr_ix: int = 0,
    write_mergefile: bool = False,
    verbose: bool = False,
) -> Optional[dict[str, list[str]]]:
    r"""
    Collect multiple logfiles of one type into one dictionary.

    Parameters
    ----------
    folder : str or pathlib.Path (or lists of that type)
        where to look for the files.
        can also be list with multiple folders..
    ext : str
        file extension.
    delimiter : str, optional
        delimiter. The default is "\t".
    colhdr_ix : int, optional
        line index where to find the column header. The default is 0.
    write_mergefile : bool, optional
        write all data to one file?. The default is False.
    verbose : bool, optional
        call some print statements. The default is False.

    Returns
    -------
    dict
        collected data.
    """
    verboseprint = print if verbose else lambda *a, **k: None
    folder = to_list_of_Path(folder)

    if not isinstance(ext, list):
        ext = [ext]

    sel_files = sorted(_get_sel_files(folder, ext))

    if not sel_files:
        return None

    verboseprint(f"loading {sel_files[0].name}")

    data = txt_2_dict(
        sel_files[0],
        delimiter=delimiter,
        colhdr_ix=colhdr_ix,
        ignore_repeated_sep=False,
        ignore_colhdr=False,
        preserve_empty=False,
    ).data

    keys = list(data.keys())  # type: ignore

    if len(sel_files) > 1:
        for i in range(1, len(sel_files)):
            verboseprint(f"loading {sel_files[i].name}")
            tmp = txt_2_dict(
                sel_files[i],
                delimiter=delimiter,
                colhdr_ix=0,
                ignore_repeated_sep=False,
                ignore_colhdr=False,
                preserve_empty=False,
            ).data
            if tmp is None:
                continue  # skip loop iteration if tmp dict is None

            keys_tmp = list(tmp.keys())  # type: ignore

            if keys_tmp == keys:  # check matching dict keys
                for k in keys:  # add data key-wise
                    data[k].extend(tmp[k])  # type: ignore
            del tmp

    if write_mergefile:  # optionally write merged data to file
        n_el = len(data[keys[0]])  # type: ignore
        outfile = pathlib.Path(
            os.path.dirname(folder[0])
            + "/"
            + os.path.basename(folder[0])
            + "_merged"
            + "/"
            + os.path.basename(folder[0])
            + "_merged_."
            + ext[0].lower()
        )
        try:  # check if directory exists
            os.stat(os.path.dirname(outfile))
        except OSError:  # create if not
            os.mkdir(os.path.dirname(outfile))

        if not outfile.exists():
            with open(outfile, "w", encoding="UTF-8") as fobj:
                fobj.write(delimiter.join(keys) + "\n")
                for i in range(n_el):
                    fobj.write(delimiter.join([data[k][i] for k in keys]) + "\n")  # type: ignore

    verboseprint("V25 logfiles import done.")

    return data  # type: ignore


###############################################################################


def collect_OSC_Logs(
    folder: Union[str, list[str], pathlib.Path, list[pathlib.Path]],
    _ext: str = "OSC",
    delimiter: str = V25_DATA_SEP,
    header_delimiter: str = " ",
    min_len: int = 6,
    ix_t_start: int = 0,
    ix_n_osc: int = 3,
    ix_col_hdr: int = 4,
    ts_fmt: str = "%d.%m.%y %H:%M:%S.%f",
    write_mergefile: bool = False,
    add_NOsc_HVSet: bool = False,
    verbose: bool = False,
) -> Optional[dict[str, list[str]]]:
    r"""
    Collect multiple logfiles of the FAIRO CL detector (OSCAR).

    Parameters
    ----------
    folder : str or pathlib.Path
        where to look for the files.
    min_len : int, optional
        minimum file lines. The default is 6.
    ix_t_start : int, optional
        line where to look for the starting time. The default is 0.
    ix_n_osc : int, optional
        line where to look for n osc parameter. The default is 3.
    ix_col_hdr : int, optional
        line where to look for the column header. The default is 4.
    header_delimiter : str, optional
        delimiter inside the header of OSC files. The default is ' '.
    delimiter : str, optional
        delimiter inside the data part. The default is '\t'.
    ts_fmt : str, optional
        format of the starting time timestamp. The default is "%d.%m.%y %H:%M:%S.%f".
    write_mergefile : bool, optional
        write all data to one file?. The default is False.
    verbose : bool, optional
        call some print statements. The default is False.

    Returns
    -------
    dict
        collected Oscar data.
    """
    verboseprint = print if verbose else lambda *a, **k: None
    folder = to_list_of_Path(folder)
    sel_files = sorted(_get_sel_files(folder, [_ext]))
    keys_data = None

    if not sel_files:
        return None

    verboseprint(f"loading {sel_files[0].name}")

    # read header
    with open(sel_files[0], "r") as file_obj:
        head = [next(file_obj) for _ in range(min_len)]

    if len(head) == min_len:
        t_start = datetime.strptime((head[ix_t_start]).strip(), ts_fmt)
        t_start = t_start.replace(tzinfo=timezone.utc).timestamp()

        Set_HV = head[ix_n_osc - 1].strip().split(header_delimiter)[-1]
        N_Oscar = head[ix_n_osc].strip().split(header_delimiter)[-1]

        # read rest of file
        osc_dat = txt_2_dict(
            sel_files[0],
            delimiter=delimiter,
            colhdr_ix=ix_col_hdr,
            keys_upper=True,
            ignore_repeated_sep=False,
            ignore_colhdr=False,
            preserve_empty=False,
        ).data

        if add_NOsc_HVSet:
            osc_dat["Set_HV"] = [Set_HV]  # type: ignore
            osc_dat["N_Oscar"] = [N_Oscar]  # type: ignore

        osc_dat["POSIX"] = [t_start + float(t) for t in osc_dat["TIME"]]  # type: ignore

        keys_data = list(osc_dat.keys())  # type: ignore

    if len(sel_files) > 1:
        for file in sel_files[1:]:
            verboseprint(f"loading {file.name}")

            with open(file, "r") as file_obj:
                head = [next(file_obj) for _ in range(min_len)]

            if len(head) == min_len:
                t_start = datetime.strptime((head[ix_t_start]).strip(), ts_fmt)
                t_start = t_start.replace(tzinfo=timezone.utc).timestamp()

                Set_HV = head[ix_n_osc - 1].strip().split(header_delimiter)[-1]
                N_Oscar = head[ix_n_osc].strip().split(header_delimiter)[-1]

                tmp = txt_2_dict(
                    file,
                    delimiter=delimiter,
                    colhdr_ix=ix_col_hdr,
                    keys_upper=True,
                    ignore_repeated_sep=False,
                    ignore_colhdr=False,
                    preserve_empty=False,
                ).data

                if add_NOsc_HVSet:
                    tmp["Set_HV"] = [Set_HV]  # type: ignore
                    tmp["N_Oscar"] = [N_Oscar]  # type: ignore

                tmp["POSIX"] = [t_start + float(t) for t in tmp["TIME"]]  # type: ignore

                keys_tmp = list(tmp.keys())  # type: ignore

                if keys_tmp == keys_data and keys_data is not None:  # check matching dict keys
                    for key in keys_data:  # add data key-wise
                        osc_dat[key].extend(tmp[key])  # type: ignore

    if write_mergefile:  # optionally write merged data to file
        keys_data = list(osc_dat.keys())  # type: ignore
        if "Set_HV" in keys_data:
            keys_data.pop(keys_data.index("Set_HV"))
        if "N_Oscar" in keys_data:
            keys_data.pop(keys_data.index("N_Oscar"))

        outfile = pathlib.Path(
            os.path.dirname(folder[0])
            + "/"
            + os.path.basename(folder[0])
            + "_merged"
            + "/"
            + os.path.basename(folder[0])
            + "_merged_.osc"
        )

        try:  # check if directory exists
            os.stat(os.path.dirname(outfile))
        except OSError:  # create if not
            os.mkdir(os.path.dirname(outfile))

        if not outfile.exists():
            with open(outfile, "w", encoding="UTF-8") as fobj:  # write the merge file
                fobj.write(delimiter.join(keys_data) + "\n")
                for i, _ in enumerate(osc_dat["POSIX"]):  # type: ignore
                    fobj.write(delimiter.join(map(str, [osc_dat[k][i] for k in keys_data])) + "\n")  # type: ignore

    verboseprint("OSC logfiles import done.")

    return osc_dat  # type: ignore
