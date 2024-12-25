# -*- coding: utf-8 -*-
"""Number to string and vice versa."""

import re
from typing import Union

import numpy as np

###############################################################################


class NumStr(object):
    """Analyse the format of a string representing a number."""

    def __init__(self, input_string, dec_sep="."):
        """
        Analyse the format of a string representing a number.

        Parameters
        ----------
        input_string : str
            String, representing a number.
        dec_sep : str, optional
            Decimal separator. The default is ".".

        Returns
        -------
        None.

        """
        self.input_string = input_string
        self.dec_sep = dec_sep
        self.regexes = {
            "dec": f"[+-]?[0-9]+[{self.dec_sep}][0-9]*|[+-]?[0-9]*[{self.dec_sep}][0-9]+",
            "no_dec": "[+-]?[0-9]+",
            "exp_dec": f"[+-]?[0-9]+[{self.dec_sep}][0-9]*[eE][+-]*[0-9]+",
            "exp_no_dec": "[+-]?[0-9]+[eE][+-]*[0-9]+",
        }

    def analyse_format(self):
        """
        Analyse the format.

        WHAT IT DOES:
            1) analyse the string to achieve a general classification
                (decimal, no decimal, exp notation)
            2) pass the string to an appropriate parsing function.

        RETURNS:
            the result of the parsing function:
                tuple with
                    format code to be used in f-string.
                    suited Python type for the number, int or float.
        """
        # 1. format definitions. key = general classification.

        # 2. analyse the format to find the general classification.
        gen_class, string = [], self.input_string.strip()
        for k, v in self.regexes.items():
            test = re.fullmatch(v, string)
            if test:
                gen_class.append(k)
        if not gen_class:
            raise TypeError("unknown format -->", string)
        elif len(gen_class) > 1:
            raise TypeError("ambiguous result -->", string, gen_class)

        # 3. based on the general classification, parse the string
        method_name = "_parse_" + str(gen_class[0])
        method = getattr(self, method_name, lambda *args: "Undefined Format!")
        return method(string)

    def _parse_dec(self, s):
        """Number is a decimal."""
        lst = s.split(self.dec_sep)
        result = "f" if not lst[1] else "." + str(len(lst[1])) + "f"
        result = "+" + result if "+" in lst[0] else result
        return (result, float)

    def _parse_no_dec(self, s):
        """Number is an integer."""
        result = "+d" if "+" in s else "d"
        return (result, int)

    def _parse_exp_dec(self, s):
        """Number is a decimal in exponential notation."""
        lst_dec = s.split(self.dec_sep)
        lst_e = lst_dec[1].upper().split("E")
        result = "." + str(len(lst_e[0])) + "E"
        result = result.lower() if "e" in s else result
        return (result, float)

    def _parse_exp_no_dec(self, s):
        """Number is in exponential notation but has no decimal points."""
        lst_e = s.upper().split("E")
        result = "+.0E" if "+" in lst_e[0] else ".0E"
        result = result.lower() if "e" in s else result
        return (result, float)


###############################################################################


def dec2str_stripped(
    num: Union[float, list, np.ndarray], dec_places: int = 3, strip: str = "right"
) -> str:
    """
    Convert floating point number to string, with zeros stripped.

    Parameters
    ----------
    num : float or list of float
        scalar or list of decimal numbers.
    dec_places : int, optional
        number of decimal places to return. defaults to 3.
    strip : string, optional
        what to strip. 'right' (default), 'left' or 'both'.

    Returns
    -------
    list of string.
        numbers formatted as strings according to specification (see kwargs).
    """
    if not isinstance(num, list):  # might be scalar or numpy array
        try:
            num = list(num)
        except TypeError:  # input was scalar
            num = [num]

    if not isinstance(dec_places, int) or int(dec_places) < 1:
        raise ValueError(f"kwarg dec_places must be integer > 1 (got {dec_places})")

    if strip == "right":
        return [f"{n:.{str(dec_places)}f}".rstrip("0") for n in num]
    if strip == "left":
        return [f"{n:.{str(dec_places)}f}".lstrip("0") for n in num]
    if strip == "both":
        return [f"{n:.{str(dec_places)}f}".strip("0") for n in num]
    raise ValueError(f"kwarg 'strip' must be 'right', 'left' or 'both' (got '{strip}')")
