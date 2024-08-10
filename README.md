[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Build Status](https://github.com/FObersteiner/pyFuppes/actions/workflows/pyfuppes-tests.yml/badge.svg)](https://github.com/FObersteiner/pyFuppes/actions/workflows/pyfuppes-tests.yml)

# pyfuppes

A collection of tools in Python. Most of it side-effect-free.

## Installation

- editable via `pip`:

  - (fork and) clone the repo, then run `pip install -e .` in the repo's directory

- from github, via pip:

  - master branch, latest commit:

    ```sh
    pip install git+https://github.com/FObersteiner/pyFuppes.git@master # alternatively @latest
    ```

  - specific tag:

    ```sh
    pip install git+https://github.com/FObersteiner/pyFuppes.git@v0.4.6
    ```

- via [poetry](https://python-poetry.org/):

  - (fork and) clone the repo, then run `poetry install` in the repo's directory

## Requirements

- currently (v0.5.0+) developed with Python 3.12. Python 3.10 and 3.11 should work (covered by github CI).
- see [pyproject.toml](https://github.com/FObersteiner/pyFuppes/blob/master/pyproject.toml)

## Content / Docs

See <https://pyfuppes.readthedocs.io/en/latest/> or go to the [API reference](https://pyfuppes.readthedocs.io/en/latest/autoapi/index.html) directly.

## License

`LGPLv3` - see LICENSE file in the root directory of the repository.
