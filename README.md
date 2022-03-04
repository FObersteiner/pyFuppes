pyfuppes
========
A collection of tools in Python.
* Free software: MIT license


Installation
============
if using `poetry`:
* (fork and) clone the repo, then run `poetry install` in the repo's directory

from `wheel` file:
* check `/dist` directory for a wheel file
* ...(fork and) clone the repo, then run `poetry build` in the repo's directory to create one for the latest version

editable via `pip`:
* (fork and) clone the repo, then `pip install -e .`


Requirements
============
* see `pyproject.toml`


Content
=======
- [avgbinmap](#module-avgbinmappy)
- [filter](#module-filterpy)
- [geo](#module-geopy)
- [misc](#module-miscpy)
- [monotonicity](#module-monotonicitypy)
- [numberstring](#module-numberstringpy)
- [plottools](#module-plottoolspy)
- [timeconversion](#module-timeconversionpy)
- [timecorr](#module-timecorrpy)
- [txt2dict](#module-txt2dictpy)


------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: avgbinmap.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **mean_angle**  
+++++++++++++++++++++++++++++++++  
```
Calculate a mean angle.
input:
    deg - (list or array) values to average
returns:
    mean of deg (float)
notes:
- if input parameter deg contains NaN or is a numpy masked array, missing
  values will be removed before the calculation.
- result is degrees between -180 and +180
```

+++++++++++++++++++++++++++++++++  
++ func + **mean_angle_numba**  
+++++++++++++++++++++++++++++++++  
```
- numba compatible version of mean_angle()
- input must be numpy array of type float!
```

+++++++++++++++++++++++++++++++++  
++ func + **mean_day_frac**  
+++++++++++++++++++++++++++++++++  
```
use the mean_angle function to calculate a mean day fraction (0-1).
the conversion to angle is necessary since day changes cannot be
  calculated as arithmetic mean.
- dfr: day fraction, 0-1
- if input parameter dfr contains NaN or is a numpy masked array, missing
  values will be removed before the calculation.
```

+++++++++++++++++++++++++++++++++  
++ func + **bin_t_10s**  
+++++++++++++++++++++++++++++++++  
```
bin a time axis to 10 s intervals around 5;
    lower boundary included, upper boundary excluded (0. <= 5. < 10.)
input:
    t - np.ndarray (time vector, unit=second, increasing monotonically)
returns:
    dict with binned time axis and bins, as returned by np.searchsorted()

keywords:
    force_t_range (bool) - True enforces bins to fall within range of t
    drop_empty (bool) - False keeps empty bins alive
```

+++++++++++++++++++++++++++++++++  
++ func + **get_npnanmean**  
+++++++++++++++++++++++++++++++++  
(no description available)

+++++++++++++++++++++++++++++++++  
++ func + **bin_y_of_t**  
+++++++++++++++++++++++++++++++++  
```
use the output of function "bin_time" or "bin_time_10s" to bin
    a variable 'v' that depends on a variable t.
input:
    v - np.ndarray to be binned
    bin_info - config dict returned by bin_time() or bin_time_10s()
returns:
    v binned according to parameters in bin_info
keywords:
    vmiss (numeric) - missing value identifier, defaults to np.NaN
    return_type (str) - how to bin, defaults to 'arit_mean'
    use_numba (bool) - use njit'ed binning functions or not
```

+++++++++++++++++++++++++++++++++  
++ func + **bin_by_pdresample**  
+++++++++++++++++++++++++++++++++  
```
use pandas DataFrame method "resample" for binning along a time axis.

Parameters
----------
t : 1d array of float or int
    time axis / independent variable.
v : 1d or 2d array corresponding to t
    dependent variable(s).
rule : string, optional
    rule for resample method. The default is '10S'.
offset : datetime.timedelta, optional
    offset to apply to the starting value.
    The default is timedelta(seconds=5).
force_t_range : boolean, optional
    truncate new time axis to min/max of t. The default is True.
drop_empty : boolean, optional
    drop empty bins that otherwise hold NaN. The default is True.

Returns
-------
df1 : pandas DataFrame
    data binned (arithmetic mean) to resampled time axis.
```

+++++++++++++++++++++++++++++++++  
++ func + **bin_by_npreduceat**  
+++++++++++++++++++++++++++++++++  
```
1D binning with numpy.add.reduceat.
ignores NaN or INF by default (finite elements only).
if ignore_nan is set to False, the whole bin will be NaN if 1 or more NaNs
    fall within the bin.
on SO:
    https://stackoverflow.com/questions/57160558/how-to-handle-nans-in-binning-with-numpy-add-reduceat
```

+++++++++++++++++++++++++++++++++  
++ func + **moving_avg**  
+++++++++++++++++++++++++++++++++  
```
simple moving average.

Parameters
----------
v : list
    data ta to average
N : integer
    number of samples per average.

Returns
-------
m_avg : list
    averaged data.
```

+++++++++++++++++++++++++++++++++  
++ func + **np_mvg_avg**  
+++++++++++++++++++++++++++++++++  
```
moving average based on numpy convolution function.

Parameters
----------
v : 1d array
    data to average.
N : integer
    number of samples per average.
ip_ovr_nan : boolean, optional
    interpolate linearly using finite elements of v. The default is False.
mode : string, optional
    config for np.convolve. The default is 'same'.
edges : string, optional
    config for output. The default is 'expand'.
        in case of mode='same', convolution gives false results
        ("running-in effect") at edges. account for this by
        simply expanding the Nth value to the edges.

Returns
-------
m_avg : 1d array
    averaged data.
```

+++++++++++++++++++++++++++++++++  
++ func + **pd_mvg_avg**  
+++++++++++++++++++++++++++++++++  
```
moving average based on pandas dataframe rolling function.

Parameters
----------
v : 1d array
    data to average.
N : integer
    number of samples per average.
ip_ovr_nan : boolean, optional
    interpolate linearly using finite elements of v. The default is False.
min_periods : TYPE, optional
    minimum number of values in averaging window. The default is 1.

Returns
-------
1d array
    averaged data.

NOTE: automatically skips NaN (forms averages over windows with <N),
      unless minimum number of values in window is exceeded.
```

+++++++++++++++++++++++++++++++++  
++ func + **sp_mvg_avg**  
+++++++++++++++++++++++++++++++++  
```
Use scipy's uniform_filter1d to calculate a moving average, see the docs at
https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.uniform_filter1d.html
Handles NaNs by removing them before interpolation.

Parameters
----------
v : np.ndarray
    data to average.
N : int
    number of samples per average.
edges : str, optional
    mode of uniform_filter1d (see docs). The default is 'nearest'.

Returns
-------
avg : np.ndarray
    averaged data.
```

+++++++++++++++++++++++++++++++++  
++ func + **map_dependent**  
+++++++++++++++++++++++++++++++++  
```
Map a variable "vcmp" depending on variable "xcmp" to an independent
    variable "xref".

Parameters
----------
xref : np.ndarray, 1D
    reference / independent variable.
xcmp : np.ndarray, 1D
    independent variable of vcmp.
vcmp : np.ndarray, 1D
    dependent variable of xcmp.
vmiss : int or float
    what should be inserted to specify missing values.
Returns
-------
vmap : np.ndarray, 1D
    vcmp mapped to xref.
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: filter.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **mask_repeated**  
+++++++++++++++++++++++++++++++++  
```
given an array a that consists of sections of repeated elements, mask
those elements in a section that repeat more than N times
on SO:
    https://stackoverflow.com/a/58482894/10197418

Parameters
----------
a : 1d array
N : int
    mask element if it repeats more than n times
atol : float, optional
    absolute tolerance to check for equality. The default is 1e-6.

Returns
-------
boolean mask
```

+++++++++++++++++++++++++++++++++  
++ func + **mask_repeated_nb**  
+++++++++++++++++++++++++++++++++  
```
numba version of mask_repeated(). Also works with input of type float.

Parameters
----------
arr : 1d array
n : int
    mask element if it repeats more than n times
atol : float, optional
    absolute tolerance to check for equality. The default is 1e-6.

Returns
-------
boolean mask
```

+++++++++++++++++++++++++++++++++  
++ func + **mask_jumps**  
+++++++++++++++++++++++++++++++++  
```
check the elements of array "arr" if the delta between element and
following element(s) exceed a threshold "trsh". How many elements to
look ahead is defined by "look_ahead"
```

+++++++++++++++++++++++++++++++++  
++ func + **filter_jumps**  
+++++++++++++++++++++++++++++++++  
```
wrapper around mask_jumps()
! interpolation assumes equidistant spacing of the independent variable of
  which arr depends !
```

+++++++++++++++++++++++++++++++++  
++ func + **filter_jumps_np**  
+++++++++++++++++++++++++++++++++  
```
if v is dependent on another variable x (e.g. time) and if that x
is not equidistant, do NOT use interpolation.

Parameters
----------
v : np 1d array
    data to filter.
max_delta : float
    defines "jump".
no_val : float, optional
    missing value placeholder. The default is np.nan.
use_abs_delta : boolean, optional
    use the absolute delta to identify jumps. The default is True.
reset_buffer_after : int, optional
    how many elements to wait until reset. The default is 3.
remove_doubles : boolean, optional
    remove elements that are repeated once. The default is False.
interpol_jumps : boolean, optional
    decide to interpolate filtered values. The default is False.
interpol_kind : string, optional
    how to interpolate, see scipy.interpolate.interp1d.
    The default is 'linear'.

Returns
-------
dict. 'filtered': filtered data
        'ix_del': idices of deleted elements
        'ix_rem': indices of remaining elements
```

+++++++++++++++++++++++++++++++++  
++ func + **del_at_edge**  
+++++++++++++++++++++++++++++++++  
```
assume v to be a 1D array which contains blocks of NaNs.
returns: v with "more NaNs", i.e. range of NaN-blocks is extended by n_cut.
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: geo.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **haversine_dist**  
+++++++++++++++++++++++++++++++++  
```
calculate Haversine distance along lat/lon coordinates.
```

+++++++++++++++++++++++++++++++++  
++ func + **geodesic_dist**  
+++++++++++++++++++++++++++++++++  
```
calculate geodesic distance along lat/lon coordinates using geopy module.
```

+++++++++++++++++++++++++++++++++  
++ func + **sza_pysolar**  
+++++++++++++++++++++++++++++++++  
```
compute solar zenith angel
uses get_altitude function from pysolar package
```

+++++++++++++++++++++++++++++++++  
++ func + **sza**  
+++++++++++++++++++++++++++++++++  
```
Returns the solar zenith angle (in degree)

UTC         (as datetime.datetime Object)
longitude   (in degree)
latitude    (in degree)

Default values: Hannover, Germany

Code adapted from https://www.python-forum.de/viewtopic.php?t=21117
(2018-10-17 8:10 UTC)
```

+++++++++++++++++++++++++++++++++  
++ func + **get_EoT**  
+++++++++++++++++++++++++++++++++  
```
input: date_ts, datetime object
returns: equation of time (float)
use for: calculation of local solar time
```

+++++++++++++++++++++++++++++++++  
++ func + **get_LSTdayFrac**  
+++++++++++++++++++++++++++++++++  
```
input:
    longitude: -180 to +180 degrees west to east, float
    tz_offset: time zone offset to UTC in hours, float
    EoT: equation of time for selected date, float
    days_delta: days since reference date, float
    time_delta: current time as days since reference date, float
returns:
    local solar time as day fraction (float, 0-1)
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: misc.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **print_progressbar**  
+++++++++++++++++++++++++++++++++  
```
https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
access: 2018-12-20
Call in a loop to create terminal progress bar
@params:
    iteration   - Required  : current iteration (Int)
    total       - Required  : total iterations (Int)
    prefix      - Optional  : prefix string (Str)
    suffix      - Optional  : suffix string (Str)
    decimals    - Optional  : positive number of decimals in percent complete (Int)
    length      - Optional  : character length of bar (Int)
    fill        - Optional  : bar fill character (Str)
```

+++++++++++++++++++++++++++++++++  
++ func + **find_youngest_file**  
+++++++++++++++++++++++++++++++++  
```
find the file that matches a pattern and has the highest modification
    timestamp if there are multiple files that match the pattern.
input:
    path, string or pathlib.Path, where to look for the file(s)
    pattern, string, pattern to look for in files (see pathlib.Path.glob)
    n, integer, how many to return. defaults to 1
returns
    filename(s) of youngest file(s), including path
    None if no file
```

+++++++++++++++++++++++++++++++++  
++ func + **checkbytes_lt128**  
+++++++++++++++++++++++++++++++++  
```
Check if all bytes of a file are less than decimal 128.
Returns True for an ASCII encoded text file.
```

+++++++++++++++++++++++++++++++++  
++ func + **find_fist_elem**  
+++++++++++++++++++++++++++++++++  
```
Find the first element in arr that gives (arr[ix] condition val) == True.
Inputs:
    arr: numeric numpy 1d array or python list
    val: scalar value
    condition: e.g. 'operator.ge' (operator package)
Returns:
    index of value matching the condition or None if no match is found.
```

+++++++++++++++++++++++++++++++++  
++ func + **list_chng_elem_index**  
+++++++++++++++++++++++++++++++++  
```
change the index of an element in a list.
! modifies the list in-place !
see https://stackoverflow.com/a/3173159/10197418
```

+++++++++++++++++++++++++++++++++  
++ func + **set_compare**  
+++++++++++++++++++++++++++++++++  
```
Compare two iterables a and b. set() is used for comparison, so only
unique elements will be considered.

Parameters
----------
a : iterable
b : iterable

Returns
-------
tuple with 3 elements:
    (what is only in a (not in b),
     what is only in b (not in a),
     what is common in a and b)
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: monotonicity.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **strictly_increasing**  
+++++++++++++++++++++++++++++++++  
```
check if elements of a list are strictly increasing.
```

+++++++++++++++++++++++++++++++++  
++ func + **strictly_decreasing**  
+++++++++++++++++++++++++++++++++  
```
check if elements of a list are strictly decreasing.
```

+++++++++++++++++++++++++++++++++  
++ func + **non_increasing**  
+++++++++++++++++++++++++++++++++  
```
check if elements of a list are increasing monotonically.
```

+++++++++++++++++++++++++++++++++  
++ func + **non_decreasing**  
+++++++++++++++++++++++++++++++++  
```
check if elements of a list are decreasing monotonically.
```

+++++++++++++++++++++++++++++++++  
++ func + **strict_inc_np**  
+++++++++++++++++++++++++++++++++  
```
check if elements of numpy 1D array are strictly increasing.
```

+++++++++++++++++++++++++++++++++  
++ func + **strict_dec_np**  
+++++++++++++++++++++++++++++++++  
```
check if elements of numpy 1D array are strictly decreasing.
```

+++++++++++++++++++++++++++++++++  
++ func + **non_inc_np**  
+++++++++++++++++++++++++++++++++  
```
check if elements of numpy 1D array are increasing monotonically.
```

+++++++++++++++++++++++++++++++++  
++ func + **non_dec_np**  
+++++++++++++++++++++++++++++++++  
```
check if elements of numpy 1D array are decreasing monotonically.
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: numberstring.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ class+ **NumStr**  
+++++++++++++++++++++++++++++++++  
```
class to hold methods for working with numbers in string format.
```

+++++++++++++++++++++++++++++++++  
++ func + **dec2str_stripped**  
+++++++++++++++++++++++++++++++++  
```
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
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: plottools.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **get_plot_range**  
+++++++++++++++++++++++++++++++++  
```
Adjust y-axis range of matplotlib pyplot for a given vector v.

Parameters
----------
v : list or numpy 1d array
    dependent variable.
add_percent : numeric type scalar value, optional
    percent of the range of v that should be added to result. The default is 5.
v_min_lim : numeric type scalar value, optional
    minimum value for lower yrange limit. The default is False.
v_max_lim : numeric type scalar value, optional
    maximum value for upper yrange limit. The default is False.
xrange : list, optional
    [lower_limit, upper_limit] of independent variable. The default is False.
x : list or numpy 1d array, optional
    independent variable. The default is False.

Returns
-------
result : list
    lower and upper limit.
```

+++++++++++++++++++++++++++++++++  
++ func + **nticks_yrange**  
+++++++++++++++++++++++++++++++++  
```
update a plot yrange so that it fits nicely into a certain number of
ticks

Parameters
----------
yrange : 2-element tuple or list
    the yrange to modify.
nticks : int
    number of ticks along y-axis.
to_multiples_of : int, optional
    make the yrange divisible w/o remainder by .... The default is 10.

Returns
-------
result : 2-element list
    updated yrange.
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: timeconversion.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **to_list**  
+++++++++++++++++++++++++++++++++  
```
convert input "parm" to a Python list object.
if "parm" is a scalar, return value "is_scalar" is True, otherwise False.
```

+++++++++++++++++++++++++++++++++  
++ func + **dtstr_2_mdns**  
+++++++++++++++++++++++++++++++++  
```
convert datetime string to seconds since midnight (float).
since a relative difference is calculated, the function is timezone-safe.

Parameters
----------
timestring : str, list of str or np.ndarray with dtype str/obj.
    timestamp given as string.
tsfmt : str, optional
    timestring format. The default is "%Y-%m-%d %H:%M:%S.%f".
ymd : tuple, optional
    starting date as tuple of integers; (year, month, day).
    The default is None.

Returns
-------
float; scalar or float; list
    seconds since midnight for the given timestring(s).
```

+++++++++++++++++++++++++++++++++  
++ func + **dtobj_2_mdns**  
+++++++++++++++++++++++++++++++++  
```
convert a Python datetime object (or list/array of ...) to seconds
after midnight.

Parameters
----------
dt_obj : datetime object or list/array of datetime objects
    the datetime to be converted to seconds after midnight.
ref_date : tuple of int, optional
    custom start date given as (year, month, day). The default is False.
ref_is_first : bool, optional
    first entry of dt_obj list/array defines start date.
    The default is False.

Returns
-------
float; scalar or list of float
    seconds after midnight for the given datetime object(s).
```

+++++++++++++++++++++++++++++++++  
++ func + **posix_2_mdns**  
+++++++++++++++++++++++++++++++++  
```
convert a POSIX timestamp (or list/array of ...) to seconds after midnight.

Parameters
----------
posixts : float, list of float or np.ndarray with dtype float.
    the POSIX timestamp to be converted to seconds after midnight.
ymd : tuple of int, optional
    define starting date as tuple of integers (year, month, day) UTC.
    The default is None, which means the reference date is that of the
    first element in posixts.

Returns
-------
float; scalar or list of float
    seconds after midnight for the given POSIX timestamp(s).
```

+++++++++++++++++++++++++++++++++  
++ func + **mdns_2_dtobj**  
+++++++++++++++++++++++++++++++++  
```
convert seconds after midnight (or list/array of ...) to datetime object.

Parameters
----------
mdns : float, list of float or np.ndarray with dtype float.
    the seconds after midnight to be converted to datetime object(s).
ref_date : tuple of int (year, month, day) or datetime object
    date that mdns refers to.
assume_UTC : boolean.
    if ref_date is supplied as a y/m/d tuple, add tzinfo UTC.
posix : bool, optional
    return POSIX timestamp(s). The default is False.
str_fmt : str, optional
    Format for datetime.strftime, e.g. "%Y-%m-%d %H:%M:%S.%f"
    If provided, output is delivered as formatted string. POSIX must
        be False in that case, or STR_FMT is overridden (evaluated last).
    The default is False.

Returns
-------
datetime object or float (POSIX timestamp)
    ...for the given seconds after midnight.
```

+++++++++++++++++++++++++++++++++  
++ func + **daysSince_2_dtobj**  
+++++++++++++++++++++++++++++++++  
```
Convert a floating point number "daysSince" to a datetime object.
day0: datetime object, from when to count.

Parameters
----------
day0 : datetime object (naive or tz-aware)
    from when to count.
daysSince : int or float
    number of days.

Returns
-------
datetime object
```

+++++++++++++++++++++++++++++++++  
++ func + **dtstr_2_posix**  
+++++++++++++++++++++++++++++++++  
```
Convert timestring without timezone information to UTC timestamp.

Parameters
----------
timestring : string
    representing date (and time).
tsfmt : str, optional
    strptime format. The default is "%Y-%m-%d %H:%M:%S.%f".
    Set to 'iso' to use Python's datetime.fromisoformat() method.
tz : timezone, optional
    The default is timezone.utc for UTC.
    Set to None to ignore/use tzinfo as parsed.
    Note: if tzinfo is None after parsing, and tz argument is None,
        Python will assume local time by default!

Returns
-------
POSIX timestamp
    UTC seconds since the epoch 1970-01-01.
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: timecorr.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **get_tcorr_parms**  
+++++++++++++++++++++++++++++++++  
```
see time_correction(); fit parameter calculation part.
```

+++++++++++++++++++++++++++++++++  
++ func + **apply_tcorr_parms**  
+++++++++++++++++++++++++++++++++  
```
see time_correction(); fit evaluation part.
```

+++++++++++++++++++++++++++++++++  
++ func + **time_correction**  
+++++++++++++++++++++++++++++++++  
```
fit a polynomial to the delta between a time vector and a
    reference time vector.
time vector is corrected by subtracting the evaluated polynomial at each
    point of the time vector.
inputs:
    t - time vector, 1D np array, numeric type
    t_ref - reference time vector, of same shape as t
    fitorder - order of the polynomial fit, integer
returns:
    dict, holding
        'fitparms': parameters of the fit, ndarray
        't_corr': corrected input time vector t
```

+++++++++++++++++++++++++++++++++  
++ func + **xcorr_timelag**  
+++++++++++++++++++++++++++++++++  
```
analyze time lag between two time series by cross-correlation.
https://en.wikipedia.org/wiki/Cross-correlation#Time_delay_analysis

Parameters
----------
x1, y1 : 1d arrays
    independend and dependent variable of reference data.
x2, y2 : 1d arrays
    independend and dependent variable of data to check for time lag.
sel_xrange : tuple
    cut data to fall within x-range "sel_xrange".
xunit : numeric, scalar value
    unit of x, seconds.
to_freq : numeric, scalar value
    interpolate data to frequency "to_freq".
rmv_NaN : boolean, optional
    clean NaNs from data. The default is True.
pad_to_zero : boolean, optional
    drag the minimum of y to zero. The default is True.
normalize_y : boolean, optional
    normalize y data to 0-1. The default is True.
show_plots : boolean, optional
    show result plot. The default is True.
corrmode : string, optional. values: 'auto', 'positive', 'negative'
     type of correlation between y1 and y2. The default is auto.
boundaries: 2-element tuple. lower and upper boundary.
    expect timelag to fall within these boundaries. The default is None.

Returns
-------
scalar value, delay in specified xunit.
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: txt2dict.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **txt_2_dict_basic**  
+++++++++++++++++++++++++++++++++  
```
most basic csv reader (delimiter-separated text file).
faster than dict reader from csv package.
input:
    file - path and filename (string or pathlib.Path)
    delimiter - line separator (string)
    offset - lines to skip at beginning (integer)
    encoding - encoding of the text file to read. default is UTF-8.
               set to None to use the operating system default.
returns:
    dict; keys = values from the first row, values = rest of the csv file.
```

+++++++++++++++++++++++++++++++++  
++ func + **txt_2_dict_simple**  
+++++++++++++++++++++++++++++++++  
```
requires input: txt file with column header and values separated by a
    specific separator (delimiter).
    file - full path to txt file.
    sep - value separator (delimiter), e.g. ";" in a csv file.
    colhdr_ix - row index of the column header.
    encoding - encoding of the text file to read. default is UTF-8.
               set to None to use the operating system default.

    to_float - set "True" if all values are represented as type float.
               otherwise, returned values are of type string.
    ignore_repeated_sep - if set to True, repeated occurrences of "sep" are
                          ignored during extraction of elements from the
                          file lines.
                          Warning: empty fields must then be filled with a
                          "no-value indicator" (e.g. string NULL)!
    keys_upper - convert key name (from column header) to upper-case
    preserve_empty - do not remove empty fields
    skip_empty_lines - ignore empty lines, just skip them.

RETURNS: dict
    {'file_hdr': list, 'data': dict with key for each col header tag}
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: nasa_ames_1001_rw.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **na1001_cls_read**  
+++++++++++++++++++++++++++++++++  
```
read NASA AMES 1001 formatted text file. expected encoding is ASCII.
args:
    file_path: path to file
kwargs:
    sep=" ": general string separator, e.g. space
    sep_com=";": string separator used exclusively in comment block
    sep_data="      ": string separator used exclusively in data block
    auto_nncoml=True: automatically determine number of lines in normal
                      comment block
    strip_lines=True: remove whitespaces from all file lines
    remove_doubleseps=False: remove repeated occurrences of general
                             separator
    vscale_vmiss_vertical=False: set to True if VSCALE and VMISS parameters
                                 are arranged vertically over multiple
                                 lines (1 entry per line) instead of in one
                                 line each (e.g. for DLR Bahamas files)
    vmiss_to_None: set True if missing values should be replaced with None.
    ensure_ascii: set True to allow only ASCII encoding (default).

returns:
    na_1001: dictionary with keys according to na1001 class.
```

+++++++++++++++++++++++++++++++++  
++ func + **na1001_cls_write**  
+++++++++++++++++++++++++++++++++  
```
write content of na1001 class instance to file in NASA AMES 1001 format.
encoding is ASCII.
inputs:
    file_path - file path, string or pathlib.Path
    na_1001 - dict containing parameters according to NASA AMES 1001 spec.
keywords:
    sep - separator (general)
    sep_com - separator used in comment section
    sep_data - separator used in data section
    crlf - newline character(s)
    overwrite - set to True to overwrite if file exists
    verbose - print info to the console
returns:
    (int) 0 -> failed, 1 -> normal write, 2 -> overwrite
```

------------------------------------------------------------------------------
------------------------------------------------------------------------------
## Module: nasa_ames_1001_tools.py
------------------------------------------------------------------------------

+++++++++++++++++++++++++++++++++  
++ func + **naDict_2_npndarr**  
+++++++++++++++++++++++++++++++++  
```
convert variables from na1001 class instance to dictionary holding
numpy arrays.

Parameters
----------
naDict : NASA AMES 1001 data in Python dict.
    ...as returned by nasa_ames_1001_read.
selVnames : list of string, optional
    VNAMEs to be converted. The default is None.
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
```

+++++++++++++++++++++++++++++++++  
++ func + **naDict_2_pddf**  
+++++++++++++++++++++++++++++++++  
```
convert variables from na1001 class instance to pandas dataframe.

Parameters
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
```
