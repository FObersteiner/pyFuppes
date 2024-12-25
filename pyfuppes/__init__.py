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
    signalsteps,
    timeconversion,
    timecorr,
    txt2dict,
    v25,
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
    "signalsteps",
    "timeconversion",
    "timecorr",
    "txt2dict",
    "v25",
)
