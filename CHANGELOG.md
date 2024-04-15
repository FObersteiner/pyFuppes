# Changelog

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
