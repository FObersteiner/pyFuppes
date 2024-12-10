[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Build Status](https://github.com/FObersteiner/pyFuppes/actions/workflows/pyfuppes-tests.yml/badge.svg)](https://github.com/FObersteiner/pyFuppes/actions/workflows/pyfuppes-tests.yml)

# pyfuppes

A collection of tools in Python. Most of it is side-effect-free (doesn't modify the input).

## Installation

- editable via `pip`:

  - (fork and) clone the repo, then run `pip install -e .` in the repo's directory

- from github, via pip (requires `git`, which you might have to install explicitly if using a virtual Python environment):

  - specific tag:

    ```sh
    pip install git+https://github.com/FObersteiner/pyFuppes.git@v0.5.1
    ```

  - master branch, latest commit (not recommended; might include unstable changes):

    ```sh
    pip install git+https://github.com/FObersteiner/pyFuppes.git@master # alternatively @latest
    ```

## Requirements

- currently (v0.5.0+) developed with Python 3.12. Python 3.10 and 3.11 should work (covered by github CI).
- see [pyproject.toml](https://github.com/FObersteiner/pyFuppes/blob/master/pyproject.toml)

## Content / Docs

See <https://pyfuppes.readthedocs.io/en/latest/> or go to the [API reference](https://pyfuppes.readthedocs.io/en/latest/autoapi/index.html) directly.

## License

`LGPLv3` - see LICENSE file in the root directory of the repository.
