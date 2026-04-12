from __future__ import annotations

import holoviews as hv
import pandas as pd

from selasviz.colormap import _CMAP_OPTIONS
from selasviz.datashader_renderer import render_datashader
from selasviz.hexbin_renderer import render_hexbin
from selasviz.scatter_renderer import (
    _normalize_category_value,
    get_discrete_colormap,
    is_categorical_column,
    render_scatter,
    resolve_color_mapping_mode,
)

hv.extension("bokeh")


def test_is_categorical_column_classification() -> None:
    assert is_categorical_column(pd.Series([True, False, True])) is True
    assert is_categorical_column(pd.Series(["a", "b", "c"])) is True
    assert is_categorical_column(pd.Series(range(10))) is True
    assert is_categorical_column(pd.Series(range(200))) is False


def test_resolve_color_mapping_mode() -> None:
    assert resolve_color_mapping_mode(pd.Series([1, 2, 3])) == "categorical"
    assert resolve_color_mapping_mode(pd.Series(range(100))) == "continuous"


def test_get_discrete_colormap_handles_edge_cases() -> None:
    assert get_discrete_colormap(0) == []

    colors = get_discrete_colormap(25)
    assert len(colors) == 25
    assert all(isinstance(color, str) for color in colors)


def test_normalize_category_value() -> None:
    assert _normalize_category_value(pd.NA) == "<NA>"
    assert _normalize_category_value(b"hello") == "hello"
    assert _normalize_category_value(123) == "123"


def test_render_scatter_uses_custom_axis_labels() -> None:
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})

    plot = render_scatter(
        df,
        "x",
        "y",
        3,
        0.6,
        "#3b82f6",
        "circle",
        "#000000",
        0.0,
        400,
        300,
        color_col=None,
        cmap_scatter="Fire",
        sc_cnorm="eq_hist",
        cmap_options=_CMAP_OPTIONS,
        x_label="log10(x)",
        y_label="log10(y)",
    )

    rendered = hv.renderer("bokeh").get_plot(plot).state

    assert rendered.xaxis[0].axis_label == "log10(x)"
    assert rendered.yaxis[0].axis_label == "log10(y)"


def test_render_hexbin_uses_custom_axis_labels() -> None:
    df = pd.DataFrame({"x": [0.0, 1.0, 2.0], "y": [0.0, 1.0, 2.0]})

    plot = render_hexbin(
        df,
        "x",
        "y",
        gridsize=10,
        min_count=0,
        alpha=0.6,
        cmap_name="Blues",
        line_color="#ffffff",
        plot_w=400,
        plot_h=300,
        cmap_options=_CMAP_OPTIONS,
        x_label="log10(x)",
        y_label="log10(y)",
    )

    rendered = hv.renderer("bokeh").get_plot(plot).state

    assert rendered.xaxis[0].axis_label == "log10(x)"
    assert rendered.yaxis[0].axis_label == "log10(y)"


def test_render_datashader_uses_custom_axis_labels() -> None:
    df = pd.DataFrame({"x": [0.0, 1.0, 2.0], "y": [0.0, 1.0, 2.0]})

    plot = render_datashader(
        df,
        "x",
        "y",
        cmap_name="Blues",
        cnorm="linear",
        spread=False,
        spread_px=1,
        plot_w=400,
        plot_h=300,
        cmap_options=_CMAP_OPTIONS,
        x_label="log10(x)",
        y_label="log10(y)",
    )

    rendered = hv.renderer("bokeh").get_plot(plot).state

    assert rendered.xaxis[0].axis_label == "log10(x)"
    assert rendered.yaxis[0].axis_label == "log10(y)"
