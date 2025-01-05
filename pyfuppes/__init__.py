from importlib import metadata

from pyfuppes import (
    avgbinmap,
    filters,
    geo,
    interpolate,
    misc,
    monotonicity,
    na1001,
    numberstring,
    plottools,
    timeconversion,
    timecorr,
    txt2dict,
)

__version__ = metadata.version("pyfuppes")

__all__ = (
    "avgbinmap",
    "filters",
    "geo",
    "interpolate",
    "misc",
    "monotonicity",
    "na1001",
    "numberstring",
    "plottools",
    "timeconversion",
    "timecorr",
    "txt2dict",
)
