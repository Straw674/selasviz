"""Scatter rendering helpers for interactive scatter plotting."""

from __future__ import annotations

from typing import Any

import colorcet as cc
import holoviews as hv
import pandas as pd


def is_categorical_column(series: pd.Series) -> bool:
    """Return whether a series should be treated as categorical.

    Parameters
    ----------
    series : pd.Series
        Source series.

    Returns
    -------
    bool
        ``True`` for bool or low-cardinality data.
    """
    if series.dtype == bool:
        return True

    if not pd.api.types.is_numeric_dtype(series):
        return True

    return series.nunique() <= 20


def resolve_color_mapping_mode(series: pd.Series) -> str:
    """Resolve color mapping mode for a series.

    Parameters
    ----------
    series : pd.Series
        Source series.

    Returns
    -------
    str
        ``"categorical"`` or ``"continuous"``.
    """
    return "categorical" if is_categorical_column(series) else "continuous"


def get_discrete_colormap(n_categories: int) -> list[str]:
    """Create a discrete colormap for categorical values.

    Parameters
    ----------
    n_categories : int
        Number of categories.

    Returns
    -------
    list[str]
        Color list with at least ``n_categories`` entries.
    """
    if n_categories <= 0:
        return []

    palette_candidates = [
        "glasbey_bw",
        "glasbey_dark",
        "glasbey",
        "tab20",
    ]
    for palette_name in palette_candidates:
        palette = cc.palette.get(palette_name)
        if not palette:
            continue

        if n_categories <= len(palette):
            return list(palette[:n_categories])

        repeats = (n_categories + len(palette) - 1) // len(palette)
        expanded_palette = list(palette) * repeats
        return expanded_palette[:n_categories]

    fallback = [
        "#1F77B4",
        "#D62728",
        "#2CA02C",
        "#9467BD",
        "#FF7F0E",
        "#8C564B",
        "#E377C2",
        "#7F7F7F",
        "#BCBD22",
        "#17BECF",
    ]
    repeats = (n_categories + len(fallback) - 1) // len(fallback)
    return (fallback * repeats)[:n_categories]


def _normalize_category_value(value: Any) -> str:
    """Normalize a scalar category value into a stable display string.

    Parameters
    ----------
    value : Any
        Raw scalar value from a categorical column.

    Returns
    -------
    str
        Stable string representation used for category coloring.
    """
    if pd.isna(value):
        return "<NA>"

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("utf-8", errors="replace")

    return str(value)


def _build_scatter_common_opts(
    size: int,
    alpha: float,
    marker: str,
    line_color: str,
    line_width: float,
    plot_w: int,
    plot_h: int,
    x_col: str,
    y_col: str,
) -> dict[str, Any]:
    """Build common scatter style options.

    Parameters
    ----------
    size : int
        Marker size.
    alpha : float
        Marker alpha.
    marker : str
        Marker style.
    line_color : str
        Marker outline color.
    line_width : float
        Marker outline width.
    plot_w : int
        Plot width.
    plot_h : int
        Plot height.
    x_col : str
        X-axis label.
    y_col : str
        Y-axis label.

    Returns
    -------
    dict[str, Any]
        Shared ``opts`` arguments for scatter plots.
    """
    return {
        "size": size,
        "alpha": alpha,
        "marker": marker,
        "line_color": line_color,
        "line_width": line_width,
        "width": plot_w,
        "height": plot_h,
        "xlabel": x_col,
        "ylabel": y_col,
        "tools": ["hover"],
        "active_tools": ["wheel_zoom"],
    }


def _render_plain_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size: int,
    alpha: float,
    color: str,
    marker: str,
    line_color: str,
    line_width: float,
    plot_w: int,
    plot_h: int,
) -> Any:
    """Render a plain scatter plot without a color column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    size : int
        Marker size.
    alpha : float
        Marker alpha.
    color : str
        Single marker color.
    marker : str
        Marker style.
    line_color : str
        Marker outline color.
    line_width : float
        Marker outline width.
    plot_w : int
        Plot width.
    plot_h : int
        Plot height.

    Returns
    -------
    Any
        HoloViews object.
    """
    points = hv.Points(df, kdims=[x_col, y_col])
    common_opts = _build_scatter_common_opts(
        size=size,
        alpha=alpha,
        marker=marker,
        line_color=line_color,
        line_width=line_width,
        plot_w=plot_w,
        plot_h=plot_h,
        x_col=x_col,
        y_col=y_col,
    )
    return points.opts(
        **common_opts,
        color=color,
        title=f"{y_col} vs {x_col}",
    )


def _render_continuous_color_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    size: int,
    alpha: float,
    marker: str,
    line_color: str,
    line_width: float,
    plot_w: int,
    plot_h: int,
    cmap_scatter: str,
    sc_cnorm: str,
    cmap_options: dict[str, list[str] | str],
) -> Any:
    """Render a scatter plot with continuous color mapping.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    color_col : str
        Continuous value column for color encoding.
    size : int
        Marker size.
    alpha : float
        Marker alpha.
    marker : str
        Marker style.
    line_color : str
        Marker outline color.
    line_width : float
        Marker outline width.
    plot_w : int
        Plot width.
    plot_h : int
        Plot height.
    cmap_scatter : str
        Colormap option name.
    sc_cnorm : str
        Color normalization mode.
    cmap_options : dict[str, list[str] | str]
        Colormap option table.

    Returns
    -------
    Any
        HoloViews object.
    """
    points = hv.Points(df, kdims=[x_col, y_col], vdims=[color_col])
    common_opts = _build_scatter_common_opts(
        size=size,
        alpha=alpha,
        marker=marker,
        line_color=line_color,
        line_width=line_width,
        plot_w=plot_w,
        plot_h=plot_h,
        x_col=x_col,
        y_col=y_col,
    )
    return points.opts(
        **common_opts,
        color=color_col,
        colorbar=True,
        colorbar_position="right",
        cmap=cmap_options[cmap_scatter],
        cnorm=sc_cnorm,
        title=f"{y_col} vs {x_col}  [color: {color_col}]",
    )


def _render_categorical_color_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    size: int,
    alpha: float,
    marker: str,
    line_color: str,
    line_width: float,
    plot_w: int,
    plot_h: int,
) -> Any:
    """Render a scatter plot with categorical color mapping.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    color_col : str
        Categorical value column for color encoding.
    size : int
        Marker size.
    alpha : float
        Marker alpha.
    marker : str
        Marker style.
    line_color : str
        Marker outline color.
    line_width : float
        Marker outline width.
    plot_w : int
        Plot width.
    plot_h : int
        Plot height.

    Returns
    -------
    Any
        HoloViews object.
    """
    categorical_series = df[color_col].map(_normalize_category_value)
    categories = [category for category in pd.unique(categorical_series)]
    palette = get_discrete_colormap(len(categories))
    color_key = {category: palette[index] for index, category in enumerate(categories)}

    category_col_name = f"__{color_col}_category"
    plot_df = df[[x_col, y_col]].copy()
    plot_df[category_col_name] = pd.Categorical(
        categorical_series, categories=categories
    )

    common_opts = _build_scatter_common_opts(
        size=size,
        alpha=alpha,
        marker=marker,
        line_color=line_color,
        line_width=line_width,
        plot_w=plot_w,
        plot_h=plot_h,
        x_col=x_col,
        y_col=y_col,
    )

    category_layers: list[hv.Points] = []
    for category in categories:
        category_df = plot_df[plot_df[category_col_name] == category]
        if category_df.empty:
            continue

        points = hv.Points(
            category_df,
            kdims=[x_col, y_col],
            vdims=[category_col_name],
            label=str(category),
        ).opts(
            **common_opts,
            color=color_key[category],
            show_legend=True,
        )
        category_layers.append(points)

    if not category_layers:
        return hv.Points(plot_df, kdims=[x_col, y_col], vdims=[category_col_name]).opts(
            **common_opts,
            color="#4ECDC4",
            show_legend=False,
            title=f"{y_col} vs {x_col}  [category: {color_col}]",
        )

    return hv.Overlay(category_layers).opts(
        title=f"{y_col} vs {x_col}  [category: {color_col}]",
        legend_position="right",
    )


def render_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size: int,
    alpha: float,
    color: str,
    marker: str,
    line_color: str,
    line_width: float,
    plot_w: int,
    plot_h: int,
    color_col: str | None,
    cmap_scatter: str,
    sc_cnorm: str,
    cmap_options: dict[str, list[str] | str],
) -> Any:
    """Render a scatter plot.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    size : int
        Marker size.
    alpha : float
        Marker alpha.
    color : str
        Single color when ``color_col`` is ``None``.
    marker : str
        Marker style.
    line_color : str
        Outline color.
    line_width : float
        Outline width.
    plot_w : int
        Plot width.
    plot_h : int
        Plot height.
    color_col : str | None
        Column for color encoding.
    cmap_scatter : str
        Colormap option name.
    sc_cnorm : str
        Color normalization for continuous values.
    cmap_options : dict[str, list[str] | str]
        Colormap option table.

    Returns
    -------
    Any
        HoloViews object.
    """
    if not color_col or color_col not in df.columns:
        return _render_plain_scatter(
            df=df,
            x_col=x_col,
            y_col=y_col,
            size=size,
            alpha=alpha,
            color=color,
            marker=marker,
            line_color=line_color,
            line_width=line_width,
            plot_w=plot_w,
            plot_h=plot_h,
        )

    mode = resolve_color_mapping_mode(df[color_col])
    if mode == "categorical":
        return _render_categorical_color_scatter(
            df=df,
            x_col=x_col,
            y_col=y_col,
            color_col=color_col,
            size=size,
            alpha=alpha,
            marker=marker,
            line_color=line_color,
            line_width=line_width,
            plot_w=plot_w,
            plot_h=plot_h,
        )

    return _render_continuous_color_scatter(
        df=df,
        x_col=x_col,
        y_col=y_col,
        color_col=color_col,
        size=size,
        alpha=alpha,
        marker=marker,
        line_color=line_color,
        line_width=line_width,
        plot_w=plot_w,
        plot_h=plot_h,
        cmap_scatter=cmap_scatter,
        sc_cnorm=sc_cnorm,
        cmap_options=cmap_options,
    )
