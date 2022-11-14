# -*- coding: utf-8 -*-
"""Tools to handle logfiles from the V25 microcontroller's memory card."""
from datetime import datetime, timezone
from itertools import chain
import os
from pathlib import Path
import platform


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
        if preserve_empty:  # only remove linefeed (if first field is empty)
            line = line[:-1] if "\n" in line else line
        else:
            line = line.strip()  # remove surrounding whitespaces
        if skip_empty_lines:
            if line == "":  # skip empty lines
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


def _to_list_of_Path(folders):
    """Turn input string or list of strings into a list of pathlib Path objects."""
    if not isinstance(folders, list):
        folders = [folders]
    return [Path(f) for f in folders]


# -----------------------------------------------------------------------------


def _insensitive_pattern(pattern):
    """Return a case-insensitive pattern to use in glob.glob or path.glob."""

    def either(c):
        return f"[{c.lower()}{c.upper()}]" if c.isalpha() else c

    return "".join(map(either, pattern))


# -----------------------------------------------------------------------------


def _get_sel_files(folders, exts, insensitive=True):
    """
    Return a generator object containing all files in "folders" having one of the extensions listed in "exts".

    Keyword "insensitive" only has an effect on Unix platforms - on Windows, glob is always case-insensitive.
    """
    msg = "all inputs must be of type list."
    assert all((isinstance(i, list) for i in (folders, exts))), msg

    if insensitive and platform.system().lower() != "windows":
        exts = [_insensitive_pattern(e) for e in exts]

    sel_files = chain()
    for f in folders:
        for e in exts:
            sel_files = chain(sel_files, f.glob(f"*{e}"))

    return sel_files


# -----------------------------------------------------------------------------


def _V25logs_cleaned_dump(path):
    """Dump an empty file signaling that this folder of V25 logfiles has been cleaned."""
    with open(path / "V25Logs_cleaned.done", "w", encoding="UTF-8") as fobj:
        fobj.write("# files in this folder were cleaned.\n")


# --- EXTERNALS ---------------------------------------------------------------


def V25Logs_cleanup(
    folder: list, exts: list, drop_info=True, check_info=True, verbose=False
):
    """
    Delete empty files and remove incomplete lines from V25 logfiles.

    Parameters
    ----------
    folder : list
        where to clean.
    exts : list
        list with file extensions specifying the files to clean.
    drop_info : bool, optional
        drop a file saying "this folder was cleaned". The default is True.
    check_info : bool, optional
        check for drop_info file. The default is True.
    verbose : true, optional
        some print-outs to the console. The default is False.

    Returns
    -------
    None.
    """
    verboseprint = print if verbose else lambda *a, **k: None
    folder = _to_list_of_Path(folder)

    if check_info:
        todo = [f for f in folder if "V25Logs_cleaned.done" not in os.listdir(f)]

    if not isinstance(exts, list):
        exts = [exts]

    if todo:

        sel_files = list(sorted(_get_sel_files(todo, exts)))

        for file in sel_files:
            with open(file, "r") as file_obj:
                data = file_obj.readlines()

            if len(data) <= 1:  # empty file or header only
                verboseprint(f"*v25_logcleaner* deleted {file.name}")
                os.remove(file)
                continue

            if data[-1][-1] != "\n":  # incomplete last line
                if len(data) <= 2:  # file would be header only if incomplete line
                    verboseprint(f"*v25_logcleaner* deleted {file.name}")
                    os.remove(file)
                    continue
                with open(file, "w", encoding="UTF-8") as file_obj:
                    file_obj.writelines(data[0:-2])
                verboseprint(f"*v25_logcleaner* deleted last line in {file.name}")

        verboseprint("*v25_logcleaner* Done.")

        if drop_info:
            for f in todo:
                if "V25Logs_cleaned.done" not in os.listdir(f):
                    _V25logs_cleaned_dump(f)
    else:
        verboseprint(f"nothing to clean in {str(folder)}")


###############################################################################


def Collect_V25Logs(
    folder, ext, delimiter="\t", colhdr_ix=0, write_mergefile=False, verbose=False
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

    sel_files = list(sorted(_get_sel_files(folder, [ext])))

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
            outfile = Path(
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


def Collect_OSC_Logs(
    folder,
    _ext="OSC",
    delimiter="\t",
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
    sel_files = list(sorted(_get_sel_files(folder, [_ext])))

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

            outfile = Path(
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
