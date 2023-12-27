[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/FObersteiner/gosyncit/blob/master/LICENSE)
[![Build Status](https://github.com/FObersteiner/pyFuppes/actions/workflows/pyfuppes-tests.yml/badge.svg)](https://github.com/FObersteiner/pyFuppes/actions/workflows/pyfuppes-tests.yml)

# pyfuppes

A collection of tools in Python.

## Installation

- from wheel file:

  - check `/dist` directory of the repo for a `*.whl` file that can be installed e.g. via `pip`

- editable via `pip`:

  - (fork and) clone the repo, then run `pip install -e .` in the repo's directory

- from github, via pip:

  - master branch, latest commit:

    ```sh
    pip install git+https://github.com/FObersteiner/pyFuppes.git@master # alternatively @latest
    ```

  - specific tag:
    ```sh
    pip install git+https://github.com/FObersteiner/pyFuppes.git@v0.3.4
    ```

- via [poetry](https://python-poetry.org/):

  - (fork and) clone the repo, then run `poetry install` in the repo's directory

## Requirements

- Python 3.9, 3.10 or 3.11. 3.12 not supported yet due to the dependency on numba.
- see [pyproject.toml](https://github.com/FObersteiner/pyFuppes/blob/master/pyproject.toml)

## Content / Docs

See https://pyfuppes.readthedocs.io/en/latest/ or directly go to [API reference](https://pyfuppes.readthedocs.io/en/latest/autoapi/index.html).
