"""UI composition helpers for interactive scatter dashboard."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
import panel as pn

WidgetMap = dict[str, Any]
ControlMap = dict[str, pn.Column]


def _detect_display_resolution() -> tuple[int, int] | None:
    """Best-effort detection of primary display resolution in pixels."""
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        width = int(root.winfo_screenwidth())
        height = int(root.winfo_screenheight())
        root.destroy()
    except Exception:
        return None

    if width <= 0 or height <= 0:
        return None
    return width, height


def _compute_auto_best_plot_size(display_w: int, display_h: int) -> int:
    """Compute an auto default for a square plot body from display resolution."""
    sidebar_and_padding_px = 520
    chrome_and_padding_px = 260

    usable_w = max(display_w - sidebar_and_padding_px, 300)
    usable_h = max(display_h - chrome_and_padding_px, 300)

    size = min(usable_w, usable_h)
    size = int(np.clip(size, 300, 1800))

    # Keep auto values aligned with slider step to avoid immediate snapping.
    return int(round(size / 50.0) * 50)


def _bind_plot_size_sync(widgets: WidgetMap) -> None:
    """Keep plot width and height synchronized while the square lock is enabled."""
    syncing = {"value": False}

    def _sync_dimension(target_name: str, value: int) -> None:
        if syncing["value"] or not widgets["plot_size_lock"].value:
            return

        target_widget = widgets[target_name]
        if target_widget.value == value:
            return

        syncing["value"] = True
        try:
            target_widget.value = value
        finally:
            syncing["value"] = False

    def _on_width_changed(event: Any) -> None:
        _sync_dimension("height", event.new)

    def _on_height_changed(event: Any) -> None:
        _sync_dimension("width", event.new)

    def _on_lock_changed(event: Any) -> None:
        if event.new:
            _sync_dimension("height", widgets["width"].value)

    widgets["width"].param.watch(_on_width_changed, "value")
    widgets["height"].param.watch(_on_height_changed, "value")
    widgets["plot_size_lock"].param.watch(_on_lock_changed, "value")
    widgets["_plot_size_sync_callbacks"] = (
        _on_width_changed,
        _on_height_changed,
        _on_lock_changed,
    )


def create_widgets(
    axis_cols: list[str],
    color_cols: list[str],
    n_rows: int,
    cmap_options: dict[str, list[str] | str],
) -> WidgetMap:
    """Create all dashboard widgets.

    Parameters
    ----------
    axis_cols : list[str]
        Numeric column names available for X/Y axes.
    color_cols : list[str]
        Column names available for scatter color encoding.
    n_rows : int
        Number of rows in the plotting dataframe.
    cmap_options : dict[str, list[str] | str]
        Colormap options.

    Returns
    -------
    dict[str, Any]
        Mapping of widget keys to widget instances.
    """
    default_plot_type = "Datashader" if n_rows >= 30000 else "Scatter"
    default_gridsize = int(np.clip(np.sqrt(n_rows) * 0.25, 10, 500))
    detected_resolution = _detect_display_resolution()
    if detected_resolution is None:
        display_w, display_h = 1920, 1080

    else:
        display_w, display_h = detected_resolution

    auto_best_size = _compute_auto_best_plot_size(display_w, display_h)
    display_text = f"Detected display: {display_w}x{display_h} \
        Adaptive size: {auto_best_size}x{auto_best_size}"

    widgets = {
        "x": pn.widgets.Select(name="X axis", options=axis_cols, value=axis_cols[0]),
        "y": pn.widgets.Select(
            name="Y axis",
            options=axis_cols,
            value=axis_cols[1] if len(axis_cols) > 1 else axis_cols[0],
        ),
        "clip_pct": pn.widgets.FloatSlider(
            name="Clip Outliers (%)",
            start=0.0,
            end=3.0,
            step=0.01,
            value=0.01,
        ),
        "x_scale": pn.widgets.Select(
            name="X axis scale",
            options=["Linear", "Log10"],
            value="Linear",
        ),
        "y_scale": pn.widgets.Select(
            name="Y axis scale",
            options=["Linear", "Log10"],
            value="Linear",
        ),
        "plot_type": pn.widgets.Select(
            name="Plot Type",
            options=["Datashader", "Hexbin", "Scatter"],
            value=default_plot_type,
        ),
        "cmap_ds": pn.widgets.Select(
            name="Colormap", options=list(cmap_options.keys()), value="Blues"
        ),
        "cmap_hex": pn.widgets.Select(
            name="Colormap", options=list(cmap_options.keys()), value="Blues"
        ),
        "alpha_scatter": pn.widgets.FloatSlider(
            name="Alpha", start=0.01, end=1.0, step=0.01, value=0.6
        ),
        "alpha_hex": pn.widgets.FloatSlider(
            name="Alpha", start=0.01, end=1.0, step=0.01, value=0.6
        ),
        "size": pn.widgets.IntSlider(
            name="Point size", start=1, end=30, step=1, value=3
        ),
        "color": pn.widgets.ColorPicker(name="Point fill color", value="#3b82f6"),
        "marker": pn.widgets.Select(
            name="Marker style",
            options=["circle", "square", "triangle", "diamond", "cross", "x"],
            value="circle",
        ),
        "line_color_scatter": pn.widgets.ColorPicker(
            name="Marker outline color", value="#000000"
        ),
        "line_width": pn.widgets.FloatSlider(
            name="Outline width", start=0.0, end=5.0, step=0.1, value=0.0
        ),
        "enable_sampling": pn.widgets.Checkbox(
            name="Auto-sample large datasets (>100k points)",
            value=True,
        ),
        "sample_size": pn.widgets.IntSlider(
            name="Sample size",
            start=2000,
            end=100000,
            step=2000,
            value=10000,
        ),
        "color_mode": pn.widgets.RadioButtonGroup(
            name="Point color mode",
            options=["Single color", "Color by column"],
            value="Single color",
            button_type="primary",
        ),
        "color_col": pn.widgets.Select(
            name="Color column", options=color_cols, value=color_cols[0]
        ),
        "cmap_scatter": pn.widgets.Select(
            name="Color column colormap",
            options=list(cmap_options.keys()),
            value="Fire",
        ),
        "scatter_cnorm": pn.widgets.Select(
            name="Color normalization (numeric columns only)",
            options=["eq_hist", "linear", "log"],
            value="eq_hist",
        ),
        "hex_gridsize": pn.widgets.IntSlider(
            name="Hexbin grid size",
            start=10,
            end=500,
            step=10,
            value=default_gridsize,
        ),
        "min_count": pn.widgets.IntSlider(
            name="Min count threshold", start=0, end=10, step=1, value=0
        ),
        "line_color_hex": pn.widgets.ColorPicker(
            name="Hex outline color", value="#ffffff"
        ),
        "cnorm": pn.widgets.Select(
            name="Color normalization",
            options=["linear", "log", "eq_hist", "cbrt"],
            value="eq_hist",
        ),
        "ds_spread": pn.widgets.Checkbox(
            name="Dynspread (expand single pixel points)", value=False
        ),
        "ds_spread_px": pn.widgets.IntSlider(
            name="Spread max px", start=1, end=10, step=1, value=1
        ),
        "plot_size_lock": pn.widgets.Checkbox(
            name="Keep 1:1 plot body ratio", value=True
        ),
        "width": pn.widgets.IntSlider(
            name="Plot width", start=100, end=3000, step=50, value=auto_best_size
        ),
        "height": pn.widgets.IntSlider(
            name="Plot height", start=100, end=2000, step=50, value=auto_best_size
        ),
        "display_info": pn.pane.Markdown(display_text),
    }
    _bind_plot_size_sync(widgets)
    return widgets


def create_controls(widgets: WidgetMap, n_rows: int) -> ControlMap:
    """Create type-specific control groups.

    Parameters
    ----------
    widgets : dict[str, Any]
        Widget mapping created by ``create_widgets``.
    n_rows : int
        Number of rows in plotting dataframe.

    Returns
    -------
    dict[str, pn.Column]
        Control group mapping.
    """
    scatter_cnorm_controls = pn.Column(widgets["scatter_cnorm"], visible=False)
    scatter_color_col_controls = pn.Column(
        widgets["color_col"],
        widgets["cmap_scatter"],
        scatter_cnorm_controls,
        visible=False,
    )
    scatter_single_color_controls = pn.Column(widgets["color"], visible=True)

    scatter_sampling_controls = pn.Column(
        widgets["enable_sampling"],
        widgets["sample_size"],
        visible=n_rows > 100000,
    )

    scatter_controls = pn.Column(
        widgets["alpha_scatter"],
        widgets["size"],
        pn.pane.Markdown("**Point color mode**", margin=(8, 0, 2, 0)),
        widgets["color_mode"],
        scatter_single_color_controls,
        scatter_color_col_controls,
        widgets["marker"],
        widgets["line_color_scatter"],
        widgets["line_width"],
        pn.layout.Divider(),
        pn.pane.Markdown("**Large dataset handling**", margin=(8, 0, 2, 0)),
        scatter_sampling_controls,
        name="Scatter options",
    )

    hexbin_controls = pn.Column(
        widgets["cmap_hex"],
        widgets["alpha_hex"],
        widgets["hex_gridsize"],
        widgets["min_count"],
        widgets["line_color_hex"],
        name="Hexbin options",
    )

    ds_controls = pn.Column(
        widgets["cmap_ds"],
        widgets["cnorm"],
        widgets["ds_spread"],
        widgets["ds_spread_px"],
        name="Datashader options",
    )

    return {
        "scatter_cnorm_controls": scatter_cnorm_controls,
        "scatter_color_col_controls": scatter_color_col_controls,
        "scatter_single_color_controls": scatter_single_color_controls,
        "scatter_sampling_controls": scatter_sampling_controls,
        "scatter_controls": scatter_controls,
        "hexbin_controls": hexbin_controls,
        "ds_controls": ds_controls,
    }


def bind_visibility_callbacks(
    widgets: WidgetMap,
    controls: ControlMap,
    pdf: pd.DataFrame,
    n_rows: int,
    resolve_mode: Callable[[pd.Series], str],
) -> None:
    """Bind visibility callbacks and initialize current visible state.

    Parameters
    ----------
    widgets : dict[str, Any]
        Widget mapping.
    controls : dict[str, pn.Column]
        Control group mapping.
    pdf : pd.DataFrame
        Numeric plotting dataframe.
    n_rows : int
        Row count of plotting dataframe.
    resolve_mode : Callable[[pd.Series], str]
        Function resolving categorical vs continuous color mode.
    """

    @pn.depends(widgets["plot_type"], watch=True)
    def _toggle_visibility(plot_type: str) -> None:
        controls["scatter_controls"].visible = plot_type == "Scatter"
        controls["hexbin_controls"].visible = plot_type == "Hexbin"
        controls["ds_controls"].visible = plot_type == "Datashader"
        controls["scatter_sampling_controls"].visible = (
            plot_type == "Scatter" and n_rows > 100000
        )

    @pn.depends(widgets["color_mode"], watch=True)
    def _toggle_color_mode(color_mode: str) -> None:
        is_col_mode = color_mode == "Color by column"
        controls["scatter_color_col_controls"].visible = is_col_mode
        controls["scatter_single_color_controls"].visible = not is_col_mode

        if is_col_mode and widgets["color_col"].value in pdf.columns:
            mode = resolve_mode(pdf[widgets["color_col"].value])
            controls["scatter_cnorm_controls"].visible = mode == "continuous"
        else:
            controls["scatter_cnorm_controls"].visible = False

    @pn.depends(widgets["color_col"], watch=True)
    def _toggle_cnorm_visibility(color_col: str) -> None:
        if (
            color_col in pdf.columns
            and widgets["color_mode"].value == "Color by column"
        ):
            mode = resolve_mode(pdf[color_col])
            controls["scatter_cnorm_controls"].visible = mode == "continuous"

    _toggle_visibility(widgets["plot_type"].value)
    _toggle_color_mode(widgets["color_mode"].value)


def create_sidebar(
    widgets: WidgetMap,
    controls: ControlMap,
    n_rows: int,
    plotted_points_pane: Any | None = None,
    reference_line_controls: Any | None = None,
) -> pn.Column:
    """Create dashboard sidebar.

    Parameters
    ----------
    widgets : dict[str, Any]
        Widget mapping.
    controls : dict[str, pn.Column]
        Control group mapping.
    n_rows : int
        Row count of plotting dataframe.
    plotted_points_pane : Any | None
        Reactive or static panel showing currently rendered point count.
    reference_line_controls : Any | None
        Optional controls for managing user-defined reference lines.

    Returns
    -------
    pn.Column
        Sidebar container.
    """
    sidebar_items: list[Any] = [
        plotted_points_pane
        if plotted_points_pane is not None
        else pn.pane.Markdown(f"## Plotted/Total Points: **{n_rows}/{n_rows}**"),
        pn.layout.Divider(),
        pn.pane.Markdown("## Axis Selection"),
        widgets["x"],
        widgets["y"],
        widgets["clip_pct"],
        pn.pane.Markdown("## Axis Scale"),
        widgets["x_scale"],
        widgets["y_scale"],
        pn.layout.Divider(),
        pn.pane.Markdown("## Plot Size"),
        widgets["display_info"],
        widgets["plot_size_lock"],
        widgets["width"],
        widgets["height"],
        pn.layout.Divider(),
        pn.pane.Markdown("## Rendering & Appearance"),
        widgets["plot_type"],
        controls["scatter_controls"],
        controls["hexbin_controls"],
        controls["ds_controls"],
    ]

    if reference_line_controls is not None:
        sidebar_items.extend(
            [
                pn.layout.Divider(),
                pn.pane.Markdown("## Reference Lines"),
                reference_line_controls,
            ]
        )

    return pn.Column(*sidebar_items, width=320)


def create_dashboard(title: str, sidebar: pn.Column, plot_panel: Any) -> pn.Column:
    """Create top-level dashboard layout.

    Parameters
    ----------
    title : str
        Dashboard title.
    sidebar : pn.Column
        Sidebar panel.
    plot_panel : Any
        Reactive plot panel.

    Returns
    -------
    pn.Column
        Full dashboard container.
    """
    layout = pn.Row(
        sidebar,
        pn.Column(
            pn.panel(plot_panel, margin=(0, 0, 0, 20)),
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    )

    header_html = (
        "<h1 style='margin-top: 5px; color: #3b82f6; font-family: sans-serif;'>"
        f"{title}</h1>"
    )
    header = pn.pane.HTML(header_html, sizing_mode="stretch_width")
    return pn.Column(header, layout, sizing_mode="stretch_width")
