# -*- coding: utf-8 -*-
"""Tools to handle logfiles from the V25 microcontroller's memory card."""
import os
import pathlib
import platform
from datetime import datetime, timezone
from itertools import chain

import tomli as toml_r

try:
    wd = pathlib.Path(__file__).parent
except NameError:
    wd = pathlib.Path.cwd()  # same as os.getcwd()
assert wd.is_dir(), "faild to obtain working directory"


# CONSTANTS -------------------------------------------------------------------

CLEANUP_DONE = "V25Logs_cleanup.done"
PATH_V25_DATA_CFG = wd / "v25_config/v25_data_cfg.toml"
V25_DATA_SEP = "\t"


# --- INTERNALS ---------------------------------------------------------------


def _txt_2_dict(
    file,
    sep=";",
    colhdr_ix=0,
    encoding="utf-8",
    ignore_repeated_sep=False,
    ignore_colhdr=False,
    keys_upper=False,
    preserve_empty=True,
    skip_empty_lines=False,
):
    """
    Convert content of a csv file to a Python dictionary.

    requires input: txt file with column header and values separated by a
        specific separator (delimiter).

        file - full path to txt file. str or pathlib.Path
        sep - value separator (delimiter), e.g. ";" in a csv file.
        colhdr_ix - row index of the column header.
        encoding - encoding of the text file to read. default is UTF-8.
                   set to None to use the operating system default.
        ignore_repeated_sep - if set to True, repeated occurrences of "sep" are
                              ignored during extraction of elements from the
                              file lines.
                              Warning: empty fields must then be filled with a
                              "no-value indicator" (e.g. string NULL)!
        keys_upper - convert key name (from column header) to upper-case
        preserve_empty - do not remove empty fields
        skip_empty_lines - ignore empty lines, just skip them.

    returns: dict
        {'file_hdr': list, 'data': dict with key for each col header tag,
         'src': path to source file}
    """
    with open(file, "r", encoding=encoding) as file_obj:
        content = file_obj.readlines()

    if not content:
        raise ValueError(f"no content in {file}")

    result = {"file_hdr": [], "data": {}, "src": str(file)}
    if colhdr_ix > 0:
        result["file_hdr"] = [line.strip() for line in content[:colhdr_ix]]

    col_hdr = content[colhdr_ix].strip().rsplit(sep)
    if ignore_repeated_sep:
        col_hdr = [s for s in col_hdr if s != ""]
    if ignore_colhdr:
        for i, _ in enumerate(col_hdr):
            col_hdr[i] = f"col_{(i+1):03d}"

    if keys_upper:
        col_hdr = [s.upper() for s in col_hdr]

    for element in col_hdr:
        result["data"][element] = []

    # cut col header...
    if ignore_colhdr:
        colhdr_ix -= 1

    content = content[1 + colhdr_ix :]
    for ix, line in enumerate(content):
        # preserve_empty: only remove linefeed (if first field is empty)
        # else: remove surrounding whitespaces
        line = line[:-1] if "\n" in line else line if preserve_empty else line.strip()

        if skip_empty_lines and line == "":  # skip empty lines
            continue

        line = line.rsplit(sep)

        if ignore_repeated_sep:
            line = [s for s in line if s != ""]

        if len(line) != len(col_hdr):
            err_msg = f"n elem in line {ix} != n elem in col header ({file})"
            raise ValueError(err_msg)
        else:  # now the actual import to the dict...
            for i, hdr_tag in enumerate(col_hdr):
                result["data"][hdr_tag].append(line[i].strip())

    return result


# -----------------------------------------------------------------------------


def _to_list_of_Path(folders: list) -> list:
    """Turn input string or list of strings into a list of pathlib Path objects."""
    if not isinstance(folders, list):
        folders = [folders]
    return [pathlib.Path(f) for f in folders]


# -----------------------------------------------------------------------------


def _insensitive_pattern(pattern: str) -> str:
    """Return a case-insensitive pattern to use in glob.glob or path.glob."""

    def either(c):
        return f"[{c.lower()}{c.upper()}]" if c.isalpha() else c

    return "".join(map(either, pattern))


# -----------------------------------------------------------------------------


def _get_sel_files(folders, file_extensions, insensitive=True):
    """
    Return a generator object containing all files in "folders" having one of the extensions listed in "file_extensions".

    Keyword "insensitive" only has an effect on Unix platforms - on Windows, glob is always case-insensitive.
    """
    msg = "all inputs must be of type list."
    assert all((isinstance(i, list) for i in (folders, file_extensions))), msg

    if insensitive and platform.system().lower() != "windows":
        file_extensions = [_insensitive_pattern(e) for e in file_extensions]

    sel_files = chain()
    for f in folders:
        for e in file_extensions:
            sel_files = chain(sel_files, f.glob(f"*{e}"))

    return sel_files


# -----------------------------------------------------------------------------


def _V25logs_cleaned_dump(path):
    """Dump an empty file signaling that this folder of V25 logfiles has been cleaned."""
    with open(path / CLEANUP_DONE, "w", encoding="UTF-8") as _:
        pass


# --- EXTERNALS ---------------------------------------------------------------


def logs_cleanup(
    directories: list,
    cfg_path: pathlib.Path = PATH_V25_DATA_CFG,
    drop_info=True,
    check_info=True,
    add_osc_datetime=True,
    verbose=False,
):
    """
    Delete empty files and remove incomplete lines from V25 logfiles.

    Parameters
    ----------
    directories : list
        where to clean.
    file_extensions : list
        list with file extensions specifying the file types to clean.
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

    directories = _to_list_of_Path(directories)

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

        # minimum lines is always 2
        if len(data) <= 2:
            verboseprint(
                f"*v25_logcleaner* deleted {file.name} which has insufficient lines"
            )
            file.unlink()
            continue

        # ensure last row has enough columns; determine from first line of data
        #   unless it's an OSC file
        if (t := file.suffix.strip(".").upper()) == "OSC":
            n_cols = cfg[t]["n_cols"]
        else:
            n_cols = len(
                [elem for elem in data[0].strip(" \n").split(V25_DATA_SEP) if elem]
            )
        while (
            len([elem for elem in data[-1].strip(" \n").split(V25_DATA_SEP) if elem])
            < n_cols
        ):
            write = True
            data = data[:-1]
            verboseprint(
                f"*v25_logcleaner* deleted last line in {file.name} which has insufficient elements"
            )

        # now check minimum lines per file type
        if (
            len(data) < cfg[file.suffix.strip(".").upper()]["min_n_lines"]
        ):  # empty file or header only
            verboseprint(
                f"*v25_logcleaner* deleted {file.name} which has insufficient lines"
            )
            file.unlink()
            continue

        # analyse the last element in the last line; compare to last element in previous line
        # TODO ?

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

        # only overwrite the file if changes must be made
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
    folder,
    ext,
    delimiter=V25_DATA_SEP,
    colhdr_ix=0,
    write_mergefile=False,
    verbose=False,
):
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
    folder = _to_list_of_Path(folder)

    sel_files = sorted(_get_sel_files(folder, [ext]))

    if sel_files:
        verboseprint(f"loading {sel_files[0].name}")

        data = _txt_2_dict(
            sel_files[0],
            sep=delimiter,
            colhdr_ix=colhdr_ix,
            ignore_repeated_sep=False,
            ignore_colhdr=False,
            preserve_empty=False,
        )["data"]

        keys = list(data.keys())

        if len(sel_files) > 1:
            for i in range(1, len(sel_files)):
                verboseprint(f"loading {sel_files[i].name}")
                tmp = _txt_2_dict(
                    sel_files[i],
                    sep=delimiter,
                    colhdr_ix=0,
                    ignore_repeated_sep=False,
                    ignore_colhdr=False,
                    preserve_empty=False,
                )["data"]
                if tmp is None:
                    continue  # skip loop iteration if tmp dict is None

                keys_tmp = list(tmp.keys())

                if keys_tmp == keys:  # check matching dict keys
                    for k in keys:  # add data key-wise
                        data[k].extend(tmp[k])
                del tmp

        if write_mergefile:  # optionally write merged data to file
            n_el = len(data[keys[0]])
            outfile = pathlib.Path(
                os.path.dirname(folder[0])
                + "/"
                + os.path.basename(folder[0])
                + "_merged"
                + "/"
                + os.path.basename(folder[0])
                + "_merged_."
                + ext.lower()
            )
            try:  # check if directory exists
                os.stat(os.path.dirname(outfile))
            except OSError:  # create if not
                os.mkdir(os.path.dirname(outfile))

            if not outfile.exists():
                with open(outfile, "w", encoding="UTF-8") as fobj:
                    fobj.write(delimiter.join(keys) + "\n")
                    for i in range(n_el):
                        fobj.write(delimiter.join([data[k][i] for k in keys]) + "\n")

        verboseprint("V25 logfiles import done.")

        return data
    return None  # no files selected


###############################################################################


def collect_OSC_Logs(
    folder,
    _ext="OSC",
    delimiter=V25_DATA_SEP,
    header_delimiter=" ",
    min_len=6,
    ix_t_start=0,
    ix_n_osc=3,
    ix_col_hdr=4,
    ts_fmt="%d.%m.%y %H:%M:%S.%f",
    write_mergefile=False,
    add_NOsc_HVSet=False,
    verbose=False,
):
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
    folder = _to_list_of_Path(folder)
    sel_files = sorted(_get_sel_files(folder, [_ext]))

    if sel_files:
        verboseprint(f"loading {sel_files[0].name}")

        # read header
        with open(sel_files[0], "r") as file_obj:
            head = [next(file_obj) for x in range(min_len)]

        if len(head) == min_len:
            t_start = datetime.strptime((head[ix_t_start]).strip(), ts_fmt)
            t_start = t_start.replace(tzinfo=timezone.utc).timestamp()

            Set_HV = head[ix_n_osc - 1].strip().split(header_delimiter)[-1]
            N_Oscar = head[ix_n_osc].strip().split(header_delimiter)[-1]

            # read rest of file
            osc_dat = _txt_2_dict(
                sel_files[0],
                sep=delimiter,
                colhdr_ix=ix_col_hdr,
                keys_upper=True,
                ignore_repeated_sep=False,
                ignore_colhdr=False,
                preserve_empty=False,
            )["data"]

            if add_NOsc_HVSet:
                osc_dat["Set_HV"] = [Set_HV]
                osc_dat["N_Oscar"] = [N_Oscar]

            osc_dat["POSIX"] = [t_start + float(t) for t in osc_dat["TIME"]]

            keys_data = list(osc_dat.keys())

        if len(sel_files) > 1:
            for file in sel_files[1:]:
                verboseprint(f"loading {file.name}")

                with open(file, "r") as file_obj:
                    head = [next(file_obj) for x in range(min_len)]

                if len(head) == min_len:
                    t_start = datetime.strptime((head[ix_t_start]).strip(), ts_fmt)
                    t_start = t_start.replace(tzinfo=timezone.utc).timestamp()

                    Set_HV = head[ix_n_osc - 1].strip().split(header_delimiter)[-1]
                    N_Oscar = head[ix_n_osc].strip().split(header_delimiter)[-1]

                    tmp = _txt_2_dict(
                        file,
                        sep=delimiter,
                        colhdr_ix=ix_col_hdr,
                        keys_upper=True,
                        ignore_repeated_sep=False,
                        ignore_colhdr=False,
                        preserve_empty=False,
                    )["data"]

                    if add_NOsc_HVSet:
                        tmp["Set_HV"] = [Set_HV]
                        tmp["N_Oscar"] = [N_Oscar]

                    tmp["POSIX"] = [t_start + float(t) for t in tmp["TIME"]]

                    keys_tmp = list(tmp.keys())

                    if keys_tmp == keys_data:  # check matching dict keys
                        for key in keys_data:  # add data key-wise
                            osc_dat[key].extend(tmp[key])

        if write_mergefile:  # optionally write merged data to file
            keys_data = list(osc_dat.keys())
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
                with open(
                    outfile, "w", encoding="UTF-8"
                ) as fobj:  # write the merge file
                    fobj.write(delimiter.join(keys_data) + "\n")
                    for i, _ in enumerate(osc_dat["POSIX"]):
                        fobj.write(
                            delimiter.join(map(str, [osc_dat[k][i] for k in keys_data]))
                            + "\n"
                        )

        verboseprint("OSC logfiles import done.")

        return osc_dat

    return None  # no files selected
