"""Datashader rendering helper for interactive scatter plotting."""

from __future__ import annotations

from typing import Any

import holoviews as hv
import pandas as pd
from holoviews.operation.datashader import datashade, dynspread


def render_datashader(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    cmap_name: str,
    cnorm: str,
    spread: bool,
    spread_px: int,
    plot_w: int,
    plot_h: int,
    cmap_options: dict[str, list[str] | str],
) -> Any:
    """Render a Datashader plot.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    cmap_name : str
        Colormap option name.
    cnorm : str
        Color normalization mode.
    spread : bool
        Whether dynspread is enabled.
    spread_px : int
        Dynspread max pixel value.
    plot_w : int
        Plot width.
    plot_h : int
        Plot height.
    cmap_options : dict[str, list[str] | str]
        Colormap option table.

    Returns
    -------
    Any
        HoloViews object.
    """
    import datashader as dslib

    points = hv.Points(df, kdims=[x_col, y_col])
    shaded = datashade(
        points,
        cmap=cmap_options[cmap_name],
        aggregator=dslib.count(),
        cnorm=cnorm,
    )

    if spread:
        shaded = dynspread(shaded, max_px=spread_px, threshold=1.0)

    return shaded.opts(
        width=plot_w,
        height=plot_h,
        title=f"{y_col} vs {x_col} (datashaded)",
        xlabel=x_col,
        ylabel=y_col,
        tools=["hover"],
        active_tools=["wheel_zoom"],
    )
