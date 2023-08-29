# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = "pyFuppes"
copyright = "2022, Florian Obersteiner"
author = "Florian Obersteiner"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autoapi_dirs = ["../pyfuppes"]

autoapi_options = [
    "members",
    "undoc-members",  # 'private-members', 'special-members',
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "**/*na1001_backend*",
    "**/*na1001_backend*/*nasa_ames_1001_rw*",
    "**/*na1001_backend*/*nasa_ames_1001_tools*",
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
