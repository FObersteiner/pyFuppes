# -*- coding: utf-8 -*-
r"""
Created on Mon Jul 22 14:03:27 2019

@author: F. Obersteiner, florian\obersteiner\\kit\edu
"""

import re


###############################################################################


class NumStr():
    """
    class to hold methods for working with numbers in string format.
    """
    def analyse_format(self, string, dec_sep='.'):
        """
        INPUT:
            s, string, representing a number
        INPUT, optional:
            dec_sep, string, decimal separator
        WHAT IT DOES:
            1) analyse the string to achieve a general classification
                (decimal, no decimal, exp notation)
            2) pass the string and the general class to an appropriate
                parsing function.

        RETURNS:
            the result of the parsing function:
                tuple with
                    format code to be used in '{}.format()'
                    suited Python type for the number, int or float.
        """

        # 1. format definitions. key = general classification.
        redct = {'dec': '[+-]?[0-9]+['+dec_sep+'][0-9]*|[+-]?[0-9]*['+dec_sep+'][0-9]+',
                 'no_dec': '[+-]?[0-9]+',
                 'exp_dec': '[+-]?[0-9]+['+dec_sep+'][0-9]*[eE][+-]*[0-9]+',
                 'exp_no_dec': '[+-]?[0-9]+[eE][+-]*[0-9]+'}

        # 2. analyse the format to find the general classification.
        gen_class, string = [], string.strip()
        for k, v in redct.items():
            test = re.fullmatch(v, string)
            if test:
                gen_class.append(k)
        if not gen_class:
            raise TypeError("unknown format -->", string)
        elif len(gen_class) > 1:
            raise TypeError("ambiguous result -->", string, gen_class)

        # 3. based on the general classification, parse the string
        method_name = 'parse_' + str(gen_class[0])
        method = getattr(self, method_name, lambda *args: "Undefined Format!")
        return method(string, *dec_sep)

    def parse_dec(self, s, dec_sep):
        """ number is a decimal... """
        lst = s.split(dec_sep)
        result = '{:f}' if not lst[1] else '{:.'+str(len(lst[1]))+'f}'
        result = result.replace(':', ':+') if '+' in lst[0] else result
        return (result, float)

    def parse_no_dec(self, s, *dec_sep):
        """ number is an integer... """
        result = '{:+d}' if '+' in s else '{:d}'
        return (result, int)

    def parse_exp_dec(self, s, dec_sep):
        """ number is a decimal in exponential notation... """
        lst_dec = s.split(dec_sep)
        lst_e = lst_dec[1].upper().split('E')
        result = '{:.'+str(len(lst_e[0]))+'E}'
        result = result.replace(':', ':+') if '+' in lst_dec[0] else result
        return (result, float)

    def parse_exp_no_dec(self, s, *dec_sep):
        """ number is in exponential notation but has no decimal points... """
        lst_e = s.upper().split('E')
        result = '{:+E}' if '+' in lst_e[0] else '{:E}'
        return (result, float)


###############################################################################


def dec2str_stripped(num, dec_places=3, strip='right'):
    """
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
    if not isinstance(num, list): # might be scalar or numpy array
        try:
            num = list(num)
        except TypeError: # input was scalar
            num = [num]

    if not isinstance(dec_places, int) or int(dec_places) < 1:
        raise ValueError(f"kwarg dec_places must be integer > 1 (got {dec_places})")

    if strip == 'right':
        return [f"{n:.{str(dec_places)}f}".rstrip('0') for n in num]
    if strip == 'left':
        return [f"{n:.{str(dec_places)}f}".lstrip('0') for n in num]
    if strip == 'both':
        return [f"{n:.{str(dec_places)}f}".strip('0') for n in num]
    raise ValueError(f"kwarg 'strip' must be 'right', 'left' or 'both' (got '{strip}')")


###############################################################################
### TESTING ###
if __name__ == '__main__':

    valid = ['45', '45.', '3E5', '4E+5', '3E-3', '2.345E+7', '-7',
              '-45.3', '-3.4E3', ' 12 ', '8.8E1', '+5.3', '+4.',
              '+10', '+2.3E121', '+4e-3','-204E-9668','.7','+.7']
    invalid = ['tesT', 'Test45', '7,7E2', '204-100', '.']

    for s in valid:
        result = NumStr().analyse_format(s)
        if isinstance(result, tuple):
            number = result[1](s)
            string = result[0].format(number)
            print('input:', s, '| number:', number, '| format:', result[0], '| output:', string)
        else:
            print('input:', s, result)

    for s in invalid:
        print(s)
        try:
            result = NumStr().analyse_format(s)
            if isinstance(result, tuple):
                number = result[1](s)
                string = result[0].format(number)
                print('input:', s, 'output:', string)
        except TypeError:
            print('TypeError!')


###############################################################################


    NUMBERS = [0.010701]
    print('right:', dec2str_stripped(NUMBERS, dec_places=3, strip='right'))
    print('left:', dec2str_stripped(NUMBERS, dec_places=3, strip='left'))
    print('both:', dec2str_stripped(NUMBERS, dec_places=3, strip='both'))
    NUMBERS = [1.0, 3.44532, 0.12011]
    print('right:', dec2str_stripped(NUMBERS, dec_places=3, strip='right'))
    print('left:', dec2str_stripped(NUMBERS, dec_places=3, strip='left'))
    print('both:', dec2str_stripped(NUMBERS, dec_places=3, strip='both'))