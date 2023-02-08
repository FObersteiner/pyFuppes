# Changelog

## v0.2.12 (2023-02-??)
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
