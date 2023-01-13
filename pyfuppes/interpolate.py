# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import polars as pl
from scipy.interpolate import interp1d


def pd_DataFrame_ip(df, new_index):
    """
    Generate a new DataFrame with all numeric columns interpolated to the new_index.

    Uses numpy's interp function.

    Parameters
    ----------
    df : pd.DataFrame
        the dataframe to be interpolated to the new index.
    new_index : pd.Index or np.array
        the new index.

    Returns
    -------
    df_out : pd.DataFrame
        a new dataframe interpolated to the new index.
    """
    # TODO: test missing !
    df_out = pd.DataFrame(index=new_index)
    df_out.index.name = df.index.name

    for colname, col in df.iteritems():
        if pd.api.types.is_numeric_dtype(col):
            df_out[colname] = np.interp(new_index, df.index, col)

    return df_out


###############################################################################


def pd_Series_ip(
    src_df: pd.DataFrame,
    dst_df: pd.DataFrame,
    ivar_src_name: str,
    dvar_src_name: str,
    ivar_dst_name: str,
    dvar_dst_name: str,
) -> pd.DataFrame:
    """
    Interpolate dependent variable from source dataframe to destination df's independent variable.

    Modifies dst_df in-place!

    Uses numpy's interp function, wrapped by scipy.interpolate.interp1d

    Returns
    -------
    df_dst : pd.DataFrame
        modified input dst_df.
    """
    # TODO: test missing !
    f = interp1d(
        src_df[ivar_src_name].values,
        src_df[dvar_src_name].values,
        kind="linear",
        bounds_error=False,
        fill_value=np.NaN,
    )
    dst_df[dvar_dst_name] = f(dst_df[ivar_dst_name])
    return dst_df


###############################################################################


def pl_Series_interp1d(
    src_df: pl.DataFrame,
    dst_df: pl.DataFrame,
    ivar_src_name: str,
    dvar_src_name: str,
    ivar_dst_name: str,
    dvar_dst_name: str,
    **kwargs,  # see https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
) -> pd.DataFrame:
    """
    Interpolate dependent variable from source dataframe to destination df's independent variable.

    Modifies dst_df in-place!

    Uses numpy's interp function, wrapped by scipy.interpolate.interp1d

    Returns
    -------
    df_dst : pl.DataFrame
        modified input dst_df.
    """
    f = interp1d(
        src_df[ivar_src_name].dt.timestamp(),
        src_df[dvar_src_name],
        **kwargs,
    )
    dst_df = dst_df.with_column(
        pl.Series(f(dst_df[ivar_dst_name])).alias(dvar_dst_name)
    )
    return dst_df


###############################################################################


def pl_Series_ip1d_lite(
    src_df: pl.DataFrame,
    dst_df: pl.DataFrame,
    ivar_src_name: str,
    dvar_src_name: str,
    ivar_dst_name: str,
    dvar_dst_name: str,
    **kwargs,  # see https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html
) -> pd.DataFrame:
    """
    Lite version of pl_Series_interp1d

    See https://stackoverflow.com/a/74819498/10197418
    """
    old = src_df[ivar_src_name].dt.timestamp().to_numpy()
    new = dst_df[ivar_dst_name].dt.timestamp().to_numpy()

    hi = np.searchsorted(old, new).clip(1, len(old) - 1)
    lo = hi - 1

    column = src_df[dvar_src_name].to_numpy()
    slope = (column[hi] - column[lo]) / (old[hi] - old[lo])

    out = pl.Series(slope * (new - old[lo]) + column[lo]).alias(dvar_dst_name)

    if (
        fill := kwargs.get("fill_value")
    ) is not None:  # cannot use None as fill_value !
        if fill != "extrapolate":
            m = (new > old.max()) | (new < old.min())
            out[m] = fill

    return dst_df.with_column(out)
