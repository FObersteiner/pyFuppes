# Changelog

<https://keepachangelog.com/>

Types of changes

- 'Added' for new features.
- 'Changed' for changes in existing functionality.
- 'Deprecated' for soon-to-be removed features.
- 'Removed' for now removed features.
- 'Fixed' for any bug fixes.
- 'Security' in case of vulnerabilities.

## [Unreleased]

## 2025-01-07, v0.6.0

Publication on the pypi.

## 2025-01-05, v0.5.3

### Removed

- v25 sub-module since V25 tools are only used by FAIROpro atm, i.e. they are better situated there
- signalsteps sub-module since unused

## 2025-01-04, v0.5.2 (re-release)

### Changed

- move from pyenv / poetry to uv
- avgbinmap.bin_y_of_t, keyword 'return_type' renamed to 'aggregation'

## 2024-09-06, v0.5.1

- geo: distance from geopy wrapper now returns array. Total distance can easily be calculated as its sum.
- txt_2_dict: fix 'preserve_empty' to actually remove surrounding delimiters
- v25_config: add H2O config (commented out)
- misc: simplify clean_path, add PCOLOR class

## 2024-07-29, v0.5.0

- drop Python 3.9 support
- add tests:
  - avgbinmap:
    - 10s binning,
    - bin y of t
    - pd resample, np reduceat
    - moving averagers
  - filters:
    - jumps
  - geo:
    - sza (comparison pysolar with own impl.)
  - interpolation:
    - pd dataframe interpolation
  - misc:
    - list change element index
    - find first elem
- remove:
  - avgbinmap.moving_avg (unused, buggy)
  - some 'isinstance' checks which should be covered by type annotations
  - misc.checkbytes_lt128 since this can be done with str.isascii() method
  - timecorr.get_tcorr_parms and .apply_tcorr_parms
- avgbinmap, binning: use namedtuple to hold time vector binning results
- filter, jumps: use namedtuple to hold filter results
- timecorr: more namedtuples
- clarify type annotations for jump filter funcs
- lof filter: fix random seed
- make pure functions, do not modify input:
  - interpolation, pd and pl Series
  - `list_change_elem_index`
- rename:
  - `list_chng_elem_index` to `list_change_elem_index`
  - `posix_2_mdns` to `unixtime_2_mdns`
  - `dtstr_2_posix` to `dtstr_2_unixtime`
  - `timecorr.time_correction` to `timecorr.correct_time`
  - `txt2dict.txt_2_dict_simple` to `txt2dict.txt_2_dict`
- simplify `dtstr_2_mdns`; now wraps `dtobj_2_mdns`
- `txt2dict.txt_2_dict`:
  - now returns a namedtuple with filepath, file header and data
  - removed option to parse elements to float. this should be done in post-processing (list(map(T, col)))
- v25:
  - use `txt_2_dict`
  - move "internal" stuff to misc

## v0.4.6 (2024-07-16)

- cleanup and test pd_Series interpolation

## v0.4.5 (2024-06-18)

- fix readthedocs generation

## v0.4.4 (2024-06-18)

- satisfy numpy 2.0 deprecations
- misc tools add path cleaner

## v0.4.3 (2024-05-17)

- add LOF filter

## v0.4.2 (2024-05-14)

- time corr, pl filters: replace comparison/fill with integers with vanilla Python timedelta
- NASA Ames 1001, reader: set ensure_ascii to False by default
- NASA Ames 1001, writer: set encoding to utf-8 by default

## v0.4.1 (2024-04-19)

- na1001: revise parameter names of df output functions (to Python standard)
- na1001: df output functions add option to clean column names
- v25: revise line cleaning in file-collector function

## v0.4.0 (2024-04-15)

- change license to LGPLv3

---

## v0.3.8 (2024-02-07)

- enable support for Python 3.12

## v0.3.7 (2024-02-07)

- v25 cleaner: add removal of ragged lines

## v0.3.6 (2024-01-05)

- expose individual modules via `__all__`

## v0.3.5 (2023-12-27)

- readme and workflow tweaks

## v0.3.4 (2023-09-24)

- adapt code to numpy 1.26 changes (xcorr-timelag function)
- na1001 / FFI1001: use today's date as default RDATE

## v0.3.3 (2023-08-28)

- function 'del_at_edge' is now 'extend_mask' and can be used to extend the 'True'
  elements in a boolean mask (tested)

## v0.3.2 (2023-08-25)

- timeconversion fix bug: xrtime_to_mdns now returns float dtype array as intended

## v0.3.1 (2023-08-21)

- na1001 fix bug: prescribe FFI to be 1001

## v0.3.1 (2023-08-16)

- na1001 refactor:
  - better pyright integration: define FFI1001 keys in `__init__` with defaults, to describe the types
  - removed `__KEYS` and \_show; now part of `__str__` and `__repr__` where needed
  - keys `HEADER` and `SRC` are now prefixed with and underscore to indicate private attrs
  - add a setter for `V`, as dependent variables are internally stored in attr `_V`

## v0.3.0 (2023-06-29)

- Python 3.11 compatible versions of numba JIT-compiled functions
- drop Python 3.8 support

---

## v0.2.14 (2023-04-17)

- avgbinmap / mean_day_frac: bugfix corner case mean day fraction is almost zero but < 0
- avgbinmap / add scipy based version of mean angle function

## v0.2.13 (2023-02-19)

- revised v25 data cleaner

## v0.2.12 (2023-02-10)

- numberstring: change output format of NumStr format analyser (to be used in f-string)

## v0.2.11 (2023-02-06)

- na1001: add option to create FFI1001 from buffered IO

## v0.2.10 (2023-02-05)

- add option to make polars df from na1001 class instance
- add 'HEADER' key to na1001 class to contain all the lines from the file header as a list

## v0.2.9 (2023-01-22)

- interpolation functions, esp. for polars Series / df

## v0.2.8 (2023-01-10)

- add `polars` helper functions (timecorr: filter non-monotonic datetime series)
- add `calc_shift` function, used for FAIRO cl timestamp re-gridding

## v0.2.7 (2022-12-21)

- NASA Ames 1001 backend updates (file format checks etc.)
- enable installation on Python 3.10

## v0.2.6 (2022-11-14)

- change of some function names in V25 tools to idiomatic ones
- change of class name pyfuppes.na1001.ffi_1001 to .FFI1001

## v0.2.5 (2022-11-14)

- include V25 tools

## v0.2.4 (2022-11-11)

- update documentation

## v0.2.3 (2022-08-29)

- update cross-correlation time lag calculator

## v0.2.2 (2022-08-29)

- add pd.Series interpolation

## v0.2.1 (2022-03-22)

- re-introduce `na1001`
- add sphinx docs

## v0.2.0 (2022-03-15)

- exclude `na1001`
