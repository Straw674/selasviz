"""Interactive 2D visualization workbench for Pandas DataFrames.

This module exposes ``launch_explorer`` as the primary constructor.
"""

from __future__ import annotations

from typing import Any

import holoviews as hv
import pandas as pd
import panel as pn

from .colormap import _CMAP_OPTIONS
from .data import (
    filter_outliers,
    prepare_plot_dataframe,
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


def _format_reference_line_label(spec: dict[str, Any]) -> str:
    """Create a compact label for a reference line spec."""
    kind = spec["kind"]
    if kind == "x = y":
        base = "x = y"
    elif kind == "x = constant":
        base = f"x = {spec['value']:.4g}"
    else:
        base = f"y = {spec['value']:.4g}"

    return f"#{spec['id']} {base} | {spec['dash']} | w={spec['width']:.2f}"


def _build_reference_line_overlay(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    reference_lines: list[dict[str, Any]],
) -> Any | None:
    """Build a line overlay from user-managed reference line specs."""
    layers: list[Any] = []

    for spec in reference_lines:
        line_opts = {
            "line_width": spec["width"],
            "line_dash": spec["dash"],
            "color": spec["color"],
        }
        kind = spec["kind"]

        if kind == "x = y":
            start = max(x_min, y_min)
            end = min(x_max, y_max)
            if start <= end:
                layers.append(hv.Curve([(start, start), (end, end)]).opts(**line_opts))
            continue

        if kind == "x = constant":
            x_value = spec["value"]
            if x_min <= x_value <= x_max:
                layers.append(hv.VLine(x_value).opts(**line_opts))
            continue

        y_value = spec["value"]
        if y_min <= y_value <= y_max:
            layers.append(hv.HLine(y_value).opts(**line_opts))

    if not layers:
        return None

    return hv.Overlay(layers)


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

    reference_lines: list[dict[str, Any]] = []
    next_ref_line_id = 1

    widgets["ref_line_kind"] = pn.widgets.Select(
        name="Line type",
        options=["x = y", "x = constant", "y = constant"],
        value="x = y",
    )
    widgets["ref_line_value"] = pn.widgets.FloatInput(
        name="Constant value",
        value=0.0,
        step=0.1,
        disabled=True,
    )
    widgets["ref_line_width"] = pn.widgets.FloatSlider(
        name="Line width",
        start=0.5,
        end=8.0,
        step=0.1,
        value=2.0,
    )
    widgets["ref_line_dash"] = pn.widgets.Select(
        name="Line style",
        options=["solid", "dashed", "dotted", "dotdash"],
        value="solid",
    )
    widgets["ref_line_color"] = pn.widgets.ColorPicker(
        name="Line color",
        value="#ef4444",
    )
    widgets["ref_line_selected"] = pn.widgets.Select(
        name="Existing lines",
        options={},
    )
    widgets["ref_line_add"] = pn.widgets.Button(
        name="Add line",
        button_type="primary",
    )
    widgets["ref_line_update"] = pn.widgets.Button(
        name="Update selected",
        button_type="default",
    )
    widgets["ref_line_remove"] = pn.widgets.Button(
        name="Remove selected",
        button_type="danger",
    )
    widgets["ref_line_revision"] = pn.widgets.IntInput(
        name="ref_line_revision",
        value=0,
        visible=False,
    )

    def _find_reference_line(line_id: int) -> dict[str, Any] | None:
        for spec in reference_lines:
            if spec["id"] == line_id:
                return spec
        return None

    def _refresh_reference_line_selector(selected_id: int | None = None) -> None:
        options = {
            _format_reference_line_label(spec): spec["id"] for spec in reference_lines
        }
        widgets["ref_line_selected"].options = options
        if selected_id is not None and selected_id in options.values():
            widgets["ref_line_selected"].value = selected_id
        elif options:
            widgets["ref_line_selected"].value = next(iter(options.values()))
        else:
            widgets["ref_line_selected"].value = None

    def _load_selected_line_to_editor(event: Any | None = None) -> None:
        line_id = widgets["ref_line_selected"].value
        if line_id is None:
            return

        spec = _find_reference_line(line_id)
        if spec is None:
            return

        widgets["ref_line_kind"].value = spec["kind"]
        widgets["ref_line_value"].disabled = spec["kind"] == "x = y"
        if spec["kind"] != "x = y":
            widgets["ref_line_value"].value = float(spec["value"])
        widgets["ref_line_width"].value = float(spec["width"])
        widgets["ref_line_dash"].value = spec["dash"]
        widgets["ref_line_color"].value = spec["color"]

    def _on_ref_line_kind_changed(event: Any) -> None:
        widgets["ref_line_value"].disabled = event.new == "x = y"

    def _bump_ref_line_revision() -> None:
        widgets["ref_line_revision"].value = widgets["ref_line_revision"].value + 1

    def _on_add_reference_line(event: Any) -> None:
        nonlocal next_ref_line_id

        kind = widgets["ref_line_kind"].value
        spec: dict[str, Any] = {
            "id": next_ref_line_id,
            "kind": kind,
            "value": float(widgets["ref_line_value"].value),
            "width": float(widgets["ref_line_width"].value),
            "dash": widgets["ref_line_dash"].value,
            "color": widgets["ref_line_color"].value,
        }
        if kind == "x = y":
            spec["value"] = 0.0

        reference_lines.append(spec)
        _refresh_reference_line_selector(selected_id=next_ref_line_id)
        next_ref_line_id += 1
        _load_selected_line_to_editor()
        _bump_ref_line_revision()

    def _on_update_reference_line(event: Any) -> None:
        line_id = widgets["ref_line_selected"].value
        if line_id is None:
            return

        spec = _find_reference_line(line_id)
        if spec is None:
            return

        kind = widgets["ref_line_kind"].value
        spec["kind"] = kind
        if kind != "x = y":
            spec["value"] = float(widgets["ref_line_value"].value)
        spec["width"] = float(widgets["ref_line_width"].value)
        spec["dash"] = widgets["ref_line_dash"].value
        spec["color"] = widgets["ref_line_color"].value

        _refresh_reference_line_selector(selected_id=line_id)
        _bump_ref_line_revision()

    def _on_remove_reference_line(event: Any) -> None:
        line_id = widgets["ref_line_selected"].value
        if line_id is None:
            return

        remaining = [spec for spec in reference_lines if spec["id"] != line_id]
        if len(remaining) == len(reference_lines):
            return

        reference_lines.clear()
        reference_lines.extend(remaining)
        _refresh_reference_line_selector()
        _load_selected_line_to_editor()
        _bump_ref_line_revision()

    widgets["ref_line_kind"].param.watch(_on_ref_line_kind_changed, "value")
    widgets["ref_line_selected"].param.watch(_load_selected_line_to_editor, "value")
    widgets["ref_line_add"].on_click(_on_add_reference_line)
    widgets["ref_line_update"].on_click(_on_update_reference_line)
    widgets["ref_line_remove"].on_click(_on_remove_reference_line)

    reference_line_controls = pn.Column(
        widgets["ref_line_selected"],
        widgets["ref_line_kind"],
        widgets["ref_line_value"],
        widgets["ref_line_width"],
        widgets["ref_line_dash"],
        widgets["ref_line_color"],
        pn.Row(widgets["ref_line_add"], widgets["ref_line_update"]),
        widgets["ref_line_remove"],
        widgets["ref_line_revision"],
    )

    controls = create_controls(widgets, n_rows)
    plotted_points_pane = pn.pane.Markdown(
        f"### Plotted/Total Points: **{n_rows:,}/{n_rows:,}**"
    )
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
        widgets["x_scale"],
        widgets["y_scale"],
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
        widgets["ref_line_revision"],
    )
    def _make_plot(
        x_col: str,
        y_col: str,
        clip_pct: float,
        x_scale: str,
        y_scale: str,
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
        ref_line_revision: int,
    ) -> Any:
        _ = ref_line_revision
        plot_df, x_label, y_label = prepare_plot_dataframe(
            pdf,
            x_col,
            y_col,
            x_scale=x_scale,
            y_scale=y_scale,
        )
        plot_df = filter_outliers(plot_df, x_col, y_col, clip_pct)

        if plot_type == "Scatter" and enable_sampling:
            plot_df = sample_large_data(
                plot_df,
                x_col,
                y_col,
                target_size=100000,
                sample_size=sample_size,
            )

        plotted_points_pane.object = (
            f"## Plotted/Total Points: **{len(plot_df)}/{n_rows}**"
        )

        if plot_type == "Datashader":
            plot = render_datashader(
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
                x_label=x_label,
                y_label=y_label,
            )
        elif plot_type == "Hexbin":
            plot = render_hexbin(
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
                x_label=x_label,
                y_label=y_label,
            )
        else:
            plot = render_scatter(
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
                x_label=x_label,
                y_label=y_label,
            )

        if plot_df.empty or not reference_lines:
            return plot

        x_min = float(plot_df[x_col].min())
        x_max = float(plot_df[x_col].max())
        y_min = float(plot_df[y_col].min())
        y_max = float(plot_df[y_col].max())

        overlay_lines = _build_reference_line_overlay(
            x_min,
            x_max,
            y_min,
            y_max,
            reference_lines,
        )
        if overlay_lines is None:
            return plot

        return plot * overlay_lines

    sidebar = create_sidebar(
        widgets,
        controls,
        n_rows,
        plotted_points_pane,
        reference_line_controls=reference_line_controls,
    )
    dashboard = create_dashboard(title, sidebar, _make_plot)

    if show:
        dashboard.show(port=port, title=title)

    return dashboard
