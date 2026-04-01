"""Interactive 2D visualization workbench for Pandas DataFrames.

This module exposes ``launch_explorer`` as the primary constructor.
"""

from __future__ import annotations

from typing import Any

import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn

from .colormap import _CMAP_OPTIONS
from .data import (
    filter_outliers,
    sample_large_data,
    select_color_candidate_columns,
    select_scalar_numeric_columns,
)
from .datashader_renderer import render_datashader
from .hexbin_renderer import render_hexbin
from .scatter_renderer import render_scatter, resolve_color_mapping_mode
from .ui import (
    bind_visibility_callbacks,
    create_controls,
    create_dashboard,
    create_sidebar,
    create_widgets,
)

hv.extension("bokeh")
pn.extension()


def launch_explorer(
    df: pd.DataFrame,
    *,
    title: str = "Data Explorer",
    port: int = 0,
    show: bool = True,
) -> pn.Column:
    """Build and optionally serve an interactive visualization dashboard.

    Parameters
    ----------
    df : pd.DataFrame
        Source data. X/Y axes use scalar numeric columns; scatter color column
        can additionally use low-cardinality string/categorical columns.
    title : str
        Browser tab and page title.
    port : int
        Port for ``dashboard.show``. ``0`` means auto-select free port.
    show : bool
        Whether to open a browser tab.

    Returns
    -------
    pn.Column
        Dashboard layout container.

    Raises
    ------
    TypeError
        If ``df`` is not a pandas DataFrame.
    ValueError
        If fewer than two scalar numeric columns are available.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")

    axis_cols = select_scalar_numeric_columns(df)
    if len(axis_cols) < 2:
        raise ValueError(
            f"Need at least 2 scalar numeric columns, got {len(axis_cols)}: {axis_cols}"
        )

    color_cols = select_color_candidate_columns(df)
    plot_cols = list(dict.fromkeys(axis_cols + color_cols))

    pdf = df[plot_cols].copy()
    n_rows = len(pdf)

    widgets = create_widgets(axis_cols, color_cols, n_rows, _CMAP_OPTIONS)
    controls = create_controls(widgets, n_rows)
    bind_visibility_callbacks(
        widgets,
        controls,
        pdf,
        n_rows,
        resolve_color_mapping_mode,
    )

    @pn.depends(
        widgets["x"],
        widgets["y"],
        widgets["clip_pct"],
        widgets["plot_type"],
        widgets["cmap_ds"],
        widgets["cmap_hex"],
        widgets["alpha_scatter"],
        widgets["alpha_hex"],
        widgets["size"],
        widgets["color"],
        widgets["marker"],
        widgets["line_color_scatter"],
        widgets["line_width"],
        widgets["hex_gridsize"],
        widgets["min_count"],
        widgets["line_color_hex"],
        widgets["cnorm"],
        widgets["ds_spread"],
        widgets["ds_spread_px"],
        widgets["width"],
        widgets["height"],
        widgets["color_mode"],
        widgets["color_col"],
        widgets["cmap_scatter"],
        widgets["scatter_cnorm"],
        widgets["enable_sampling"],
        widgets["sample_size"],
    )
    def _make_plot(
        x_col: str,
        y_col: str,
        clip_pct: float,
        plot_type: str,
        cmap_ds: str,
        cmap_hex: str,
        alpha_sc: float,
        alpha_hex: float,
        pt_size: int,
        pt_color: str,
        pt_marker: str,
        sc_line_color: str,
        sc_line_width: float,
        hex_gridsize: int,
        hex_min_count: int,
        hex_line_color: str,
        ds_cnorm: str,
        ds_spread: bool,
        ds_spread_px: int,
        plot_w: int,
        plot_h: int,
        color_mode: str,
        color_col: str,
        cmap_scatter: str,
        sc_cnorm: str,
        enable_sampling: bool,
        sample_size: int,
    ) -> Any:
        plot_df = filter_outliers(pdf, x_col, y_col, clip_pct)

        if plot_type == "Scatter" and enable_sampling:
            plot_df = sample_large_data(
                plot_df,
                x_col,
                y_col,
                target_size=100000,
                sample_size=sample_size,
            )

        if plot_type == "Datashader":
            return render_datashader(
                plot_df,
                x_col,
                y_col,
                cmap_ds,
                ds_cnorm,
                ds_spread,
                ds_spread_px,
                plot_w,
                plot_h,
                _CMAP_OPTIONS,
            )

        if plot_type == "Hexbin":
            return render_hexbin(
                plot_df,
                x_col,
                y_col,
                hex_gridsize,
                hex_min_count,
                alpha_hex,
                cmap_hex,
                hex_line_color,
                plot_w,
                plot_h,
                _CMAP_OPTIONS,
            )

        return render_scatter(
            plot_df,
            x_col,
            y_col,
            pt_size,
            alpha_sc,
            pt_color,
            pt_marker,
            sc_line_color,
            sc_line_width,
            plot_w,
            plot_h,
            color_col=color_col if color_mode == "Color by column" else None,
            cmap_scatter=cmap_scatter,
            sc_cnorm=sc_cnorm,
            cmap_options=_CMAP_OPTIONS,
        )

    sidebar = create_sidebar(widgets, controls, n_rows)
    dashboard = create_dashboard(title, sidebar, _make_plot)

    if show:
        dashboard.show(port=port, title=title)

    return dashboard


if __name__ == "__main__":
    rng = np.random.default_rng(27)
    n = 50000
    demo_df = pd.DataFrame(
        {
            "ra": rng.uniform(200, 220, n),
            "dec": rng.uniform(40, 50, n),
            "redshift": rng.uniform(0.05, 0.8, n),
            "mass": 10 ** rng.uniform(13, 15, n),
            "richness": rng.integers(10, 200, n),
            "name": [f"CLJ{i:05d}" for i in range(n)],
        }
    )
    launch_explorer(demo_df, title="Demo Explorer")
