# -*- coding: utf-8 -*-
"""Text file to dictionary."""

from pathlib import Path
from typing import NamedTuple, Union

###############################################################################


def txt_2_dict_basic(
    file: Union[str, Path], delimiter: str, *, offset: int = 0, encoding: str = "utf-8"
) -> dict[str, list[str]]:
    """
    Most basic csv reader (delimiter-separated text file).

    Faster than dict reader from csv package.

    Input:
    file - path and filename (string or pathlib.Path)
    delimiter - line separator (string)
    offset - lines to skip at beginning (integer)
    encoding - encoding of the text file to read. default is UTF-8.
               set to None to use the operating system default.

    Returns:
        dict; keys = values from the first row, values = rest of the csv file.
    """
    with open(file, "r", encoding=encoding) as csvfile:
        data = csvfile.read().splitlines()
    if offset > 0:
        data = data[offset:]

    separated = []
    for line in data:
        separated.append([v for v in line.split(delimiter) if v])

    return {item[0]: list(item[1:]) for item in zip(*separated)}


###############################################################################

CsvData = NamedTuple(
    "csv_data",
    [
        ("src", str),
        ("file_hdr", list[str]),
        ("data", dict[str, list[str]]),
    ],
)


def txt_2_dict(
    file: Union[str, Path],
    delimiter: str = ";",
    colhdr_ix: int = 0,
    encoding: str = "utf-8",
    ignore_repeated_sep: bool = False,
    ignore_colhdr: bool = False,
    keys_upper: bool = False,
    preserve_empty: bool = True,
    skip_empty_lines: bool = False,
) -> CsvData:
    """
    Read csv with header.

    Input: txt file with column header and values separated by a specific separator (delimiter).

    file                - full path to txt file.
    delimiter           - value separator (delimiter), e.g. ";" in a csv file.
    colhdr_ix           - row index of the column header.
    encoding            - encoding of the text file to read. default is UTF-8.
                          set to None to use the operating system default.
    ignore_repeated_sep - if set to True, repeated occurrences of delimiter are
                          ignored during extraction of elements from the
                          file lines
                          Warning: empty fields must then be filled with a
                          "no-value indicator" (e.g. string NULL)
    keys_upper          - convert key name (from column header) to upper-case
    preserve_empty      - do not remove empty fields
    skip_empty_lines    - ignore empty lines, just skip them

    Returns:
      NamedTuple 'CsvData';
        .src      - file path, str
        .file_hdr - file header (if any), list of str
        .data     - dict[str list[str]]
    """

    with open(file, "r", encoding=encoding) as file_obj:
        content = file_obj.readlines()

    if not content:
        raise ValueError(f"no content in {file}")

    result = {"file_hdr": [], "data": {}, "src": file if isinstance(file, str) else file.as_posix()}

    if colhdr_ix > 0:
        result["file_hdr"] = [line.strip() for line in content[:colhdr_ix]]

    col_hdr = content[colhdr_ix].strip().rsplit(delimiter)
    if ignore_repeated_sep:
        col_hdr = [s for s in col_hdr if s != ""]
    if ignore_colhdr:
        for i, _ in enumerate(col_hdr):
            col_hdr[i] = f"col_{(i+1):03d}"

    if keys_upper:
        col_hdr = [s.upper() for s in col_hdr]

    for element in col_hdr:
        result["data"][element] = []

    if ignore_colhdr:  # cut col header...
        colhdr_ix -= 1

    content = content[1 + colhdr_ix :]
    for ix, line in enumerate(content):
        # preserve_empty: only remove linefeed (if first field is empty)
        # else: remove surrounding whitespaces
        line = line[:-1] if "\n" in line else line if preserve_empty else line.strip()

        if skip_empty_lines and line == "":  # skip empty lines
            continue

        line = line.rsplit(delimiter)

        if ignore_repeated_sep:
            line = [s for s in line if s != ""]

        if len(line) != len(col_hdr):
            err_msg = f"{len(line)} elements in line {ix + 1 + colhdr_ix} != {len(col_hdr)} elem in col header ({file}).\nLine content: {line}"
            raise ValueError(err_msg)

        for i, hdr_tag in enumerate(col_hdr):
            result["data"][hdr_tag].append(line[i].strip())

    return CsvData(result["src"], result["file_hdr"], result["data"])
