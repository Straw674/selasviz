"""Hexbin rendering helper for interactive scatter plotting."""

from __future__ import annotations

from typing import Any

import holoviews as hv
import pandas as pd


def render_hexbin(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    gridsize: int,
    min_count: int,
    alpha: float,
    cmap_name: str,
    line_color: str,
    plot_w: int,
    plot_h: int,
    cmap_options: dict[str, list[str] | str],
) -> Any:
    """Render a hexbin plot.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    gridsize : int
        Hexbin grid size.
    min_count : int
        Minimum count threshold.
    alpha : float
        Plot alpha.
    cmap_name : str
        Colormap option name.
    line_color : str
        Hex outline color.
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
    hexbins = hv.HexTiles(df, kdims=[x_col, y_col])

    opts_dict: dict[str, Any] = {
        "gridsize": gridsize,
        "min_count": min_count,
        "alpha": alpha,
        "cmap": cmap_options[cmap_name],
        "width": plot_w,
        "height": plot_h,
        "title": f"{y_col} vs {x_col} (hexbin)",
        "xlabel": x_col,
        "ylabel": y_col,
        "tools": ["hover"],
        "active_tools": ["wheel_zoom"],
    }
    if line_color:
        opts_dict["line_color"] = line_color

    return hexbins.opts(**opts_dict)
