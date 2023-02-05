# -*- coding: utf-8 -*-
"""NA read/write."""

import os
from datetime import date
from pathlib import Path


###############################################################################


def na1001_cls_read(
    input_data,
    sep=" ",
    sep_com=";",  # obsolete
    sep_data="\t",
    auto_nncoml=True,
    strip_lines=True,
    rmv_repeated_seps=False,
    vscale_vmiss_vertical=False,
    vmiss_to_None=False,
    ensure_ascii=True,
):
    """
    Read NASA Ames 1001 formatted text file. Expected encoding is ASCII.

    See class method for detailled docstring.
    """
    try:
        data = input_data.getvalue()  # works on io.StringIO
    except AttributeError:
        if isinstance(input_data, str):  # file path is provided as string; need Path
            input_data = Path(input_data)

        if not input_data.is_file():  # check if file exists
            raise FileExistsError(str(input_data) + "\n    does not exist.")

        # by definition, NASA Ames 1001 is pure ASCII. the following lines allow
        # to read files with other encodings; use with caution
        encodings = (
            ("ascii",) if ensure_ascii else ("ascii", "utf-8", "cp1252", "latin-1")
        )
        data = None
        for enc in encodings:
            try:
                with open(input_data, "r", encoding=enc) as file_obj:
                    data = file_obj.readlines()  # read file content to string list
            except ValueError:  # invalid encoding, try next
                pass
            else:
                if enc != "ascii":
                    print(
                        f"warning: non-ascii encoding '{enc}' used in file {input_data.name}"
                    )
                break  # found a working encoding
        if not data:
            raise ValueError(
                f"could not decode {input_data.name} (ASCII-only: {ensure_ascii})"
            )

        na_1001 = {"SRC": input_data.as_posix()}

    if strip_lines:
        for i, line in enumerate(data):
            data[i] = line.strip()

    if rmv_repeated_seps:
        for i, line in enumerate(data):
            while sep + sep in line:
                line = line.replace(sep + sep, sep)
            data[i] = line

    tmp = list(map(int, data[0].split()))
    assert len(tmp) == 2, f"invalid format in line 1: '{data[0]}'"
    assert (
        tmp[0] >= 15
    ), f"NASA Ames FFI 1001 has a least 15 header lines (specified: {tmp[0]})"
    assert tmp[1] == 1001, f"invalid FFI in line 1 '{data[0]}'"

    nlhead = tmp[0]
    na_1001["NLHEAD"] = nlhead
    na_1001["_FFI"] = tmp[1]

    header = data[:nlhead]
    data = data[nlhead:]
    if data == [""] or data == ["\n"]:
        data = None

    # test case: no data ->
    assert data, "no data found."

    na_1001["ONAME"] = header[1]
    na_1001["ORG"] = header[2]
    na_1001["SNAME"] = header[3]
    na_1001["MNAME"] = header[4]

    tmp = list(map(int, header[5].split()))
    assert len(tmp) == 2, f"invalid format in line 6: '{header[5]}'"
    na_1001["IVOL"], na_1001["NVOL"] = tmp[0], tmp[1]

    tmp = list(map(int, header[6].split()))
    assert len(tmp) == 6, f"invalid format line 7: '{header[6]}'"

    # check for valid date in line 7 (yyyy mm dd)
    assert date(*tmp[:3]) <= date(*tmp[3:6]), "RDATE must be greater or equal to DATE"
    na_1001["DATE"], na_1001["RDATE"] = tmp[:3], tmp[3:6]

    # DX check if the line contains a decimal separator; if so use float else int
    na_1001["DX"] = float(header[7]) if "." in header[7] else int(header[7])
    na_1001["XNAME"] = header[8]  # .rsplit(sep=sep_com)

    n_vars = int(header[9])
    na_1001["NV"] = n_vars

    if vscale_vmiss_vertical:
        offset = n_vars * 2
        na_1001["VSCAL"] = header[10 : 10 + n_vars]
        na_1001["VMISS"] = header[10 + n_vars : 10 + n_vars * 2]
    else:
        offset = 2
        na_1001["VSCAL"] = header[10].split()
        na_1001["VMISS"] = header[11].split()

    assert (
        len(na_1001["VSCAL"]) == na_1001["NV"]
    ), f"number of elements in VSCAL (have: {len(na_1001['VSCAL'])}) must match number of variables specified ({na_1001['NV']})"
    assert (
        len(na_1001["VMISS"]) == na_1001["NV"]
    ), f"number of elements in VMISS (have: {len(na_1001['VMISS'])}) must match number of variables specified ({na_1001['NV']})"
    assert (
        n_vars == len(na_1001["VSCAL"]) == len(na_1001["VMISS"])
    ), "VSCAL, VMISS and NV must have equal number of elements"

    na_1001["_VNAME"] = header[10 + offset : 10 + n_vars + offset]

    nscoml = int(header[10 + n_vars + offset])
    na_1001["NSCOML"] = nscoml
    if nscoml > 0:  # read special comment if nscoml>0
        na_1001["_SCOM"] = header[n_vars + 11 + offset : n_vars + nscoml + 11 + offset]
    else:
        na_1001["_SCOM"] = ""

    msg = "nscoml not equal n elements in list na_1001['_SCOM']"
    assert nscoml == len(na_1001["_SCOM"]), msg

    # read normal comment if nncoml>0
    if auto_nncoml is True:
        nncoml = nlhead - (n_vars + nscoml + 12 + offset)
    else:
        nncoml = int(header[n_vars + nscoml + 11 + offset])
    na_1001["NNCOML"] = nncoml

    if nncoml > 0:
        na_1001["_NCOM"] = header[
            n_vars + nscoml + 12 + offset : n_vars + nscoml + nncoml + 12 + offset
        ]
    else:
        na_1001["_NCOM"] = ""

    msg = "nncoml not equal n elements in list na_1001['_NCOM']"
    assert nncoml == len(na_1001["_NCOM"]), msg

    msg = "nlhead must be equal to nncoml + nscoml + n_vars + 14"
    assert nncoml + nscoml + n_vars + 14 == nlhead, msg

    # done with header, we can set HEADER variable now
    na_1001["HEADER"] = header

    # continue with variables
    na_1001["_X"] = []  # holds independent variable
    na_1001["V"] = [[] for _ in range(n_vars)]  # list for each dependent variable

    for ix, line in enumerate(data):
        if line == "" or line == "\n":  # skip empty lines or trailing newline
            continue

        parts = line.rsplit(sep=sep_data)
        assert (
            len(parts) == n_vars + 1
        ), f"invalid number of parameters in line {ix+nlhead+1}, have {len(parts)} ({parts}), want {n_vars+1}"

        na_1001["_X"].append(parts[0].strip())
        if vmiss_to_None:
            for j in range(n_vars):
                na_1001["V"][j].append(
                    parts[j + 1].strip()
                    if parts[j + 1].strip() != na_1001["VMISS"][j]
                    else None
                )
        else:
            for j in range(n_vars):
                na_1001["V"][j].append(parts[j + 1].strip())

    return na_1001


###############################################################################


def na1001_cls_write(
    file_path,
    na_1001,
    sep=" ",
    sep_com=";",  # obsolete
    sep_data="\t",
    overwrite=0,
    verbose=False,
):
    """
    Write content of na1001 class instance to file in NASA Ames 1001 format. Encoding is ASCII.

    See class method for detailled docstring.
    """
    verboseprint = print if verbose else lambda *a, **k: None

    # check if directory exists, create if not.
    if not os.path.isdir(os.path.dirname(file_path)):
        os.mkdir(os.path.dirname(file_path))

    # check if file exists, act according to overwrite keyword
    if os.path.isfile(file_path):
        if not overwrite:
            verboseprint(
                f"write failed: {file_path} already exists.\n"
                "set overwrite keyword to overwrite."
            )
            return 0  # write failed / forbidden
        write = 2  # overwriting
    write = 1  # normal writing

    # check n variables and comment lines; adjust values if incorrect
    n_vars_named = len(na_1001["_VNAME"])
    n_vars_data = len(na_1001["V"])
    if n_vars_named != n_vars_data:
        raise ValueError(
            "NA error: n vars in V and VNAME not equal, "
            f"{n_vars_data} vs. {n_vars_named}!"
        )

    if n_vars_named - na_1001["NV"] != 0:
        verboseprint("NA output: NV corrected")
        na_1001["NV"] = n_vars_named

    nscoml_is = len(na_1001["_SCOM"])
    if (nscoml_is - na_1001["NSCOML"]) != 0:
        verboseprint("NA output: NSCOML corrected")
        na_1001["NSCOML"] = nscoml_is

    nncoml_is = len(na_1001["_NCOM"])
    if (nncoml_is - na_1001["NNCOML"]) != 0:
        verboseprint("NA output: NNCOML corrected")
        na_1001["NNCOML"] = nncoml_is

    nlhead_is = 14 + n_vars_named + nscoml_is + nncoml_is
    if (nlhead_is - na_1001["NLHEAD"]) != 0:
        verboseprint("NA output: NLHEAD corrected")
        na_1001["NLHEAD"] = nlhead_is

    # begin the actual writing process
    with open(file_path, "w", encoding="ascii") as file_obj:
        block = str(na_1001["NLHEAD"]) + sep + str(na_1001["_FFI"]) + "\n"
        file_obj.write(block)

        block = str(na_1001["ONAME"]) + "\n"
        file_obj.write(block)

        block = str(na_1001["ORG"]) + "\n"
        file_obj.write(block)

        block = str(na_1001["SNAME"]) + "\n"
        file_obj.write(block)

        block = str(na_1001["MNAME"]) + "\n"
        file_obj.write(block)

        block = str(na_1001["IVOL"]) + sep + str(na_1001["NVOL"]) + "\n"
        file_obj.write(block)

        # dates: assume "yyyy m d" in tuple
        block = (
            "%4.4u" % na_1001["DATE"][0]
            + sep
            + "%2.2u" % na_1001["DATE"][1]
            + sep
            + "%2.2u" % na_1001["DATE"][2]
            + sep
            + "%4.4u" % na_1001["RDATE"][0]
            + sep
            + "%2.2u" % na_1001["RDATE"][1]
            + sep
            + "%2.2u" % na_1001["RDATE"][2]
            + "\n"
        )
        file_obj.write(block)

        file_obj.write(f"{na_1001['DX']}" + "\n")

        # obsolete: CARIBIC
        # file_obj.write(sep_com.join(na_1001["XNAME"]) + "\n")
        file_obj.write(na_1001["XNAME"] + "\n")

        n_vars = na_1001["NV"]  # get number of variables
        block = str(n_vars) + "\n"
        file_obj.write(block)

        line = ""
        for i in range(n_vars):
            line += str(na_1001["VSCAL"][i]) + sep
        if line.endswith("\n"):
            line = line[0:-1]
        else:
            line = line[0:-1] + "\n"
        file_obj.write(line)

        line = ""
        for i in range(n_vars):
            line += str(na_1001["VMISS"][i]) + sep
        if line.endswith("\n"):
            line = line[0:-1]
        else:
            line = line[0:-1] + "\n"
        file_obj.write(line)

        block = na_1001["_VNAME"]
        for i in range(n_vars):
            file_obj.write(block[i] + "\n")

        nscoml = na_1001["NSCOML"]  # get number of special comment lines
        line = str(nscoml) + "\n"
        file_obj.write(line)

        block = na_1001["_SCOM"]
        for i in range(nscoml):
            file_obj.write(block[i] + "\n")

        nncoml = na_1001["NNCOML"]  # get number of normal comment lines
        line = str(nncoml) + "\n"
        file_obj.write(line)

        block = na_1001["_NCOM"]
        for i in range(nncoml):
            file_obj.write(block[i] + "\n")

        for i, x in enumerate(na_1001["_X"]):
            line = str(x) + sep_data
            for j in range(n_vars):
                line += str(na_1001["V"][j][i]) + sep_data
            file_obj.write(line[0:-1] + "\n")

    return write


###############################################################################
