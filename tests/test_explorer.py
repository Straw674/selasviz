from __future__ import annotations

import holoviews as hv

from selasviz.explorer import (
    _build_reference_line_overlay,
    _format_reference_line_label,
)

hv.extension("bokeh")


def test_format_reference_line_label_for_all_kinds() -> None:
    diag_label = _format_reference_line_label(
        {
            "id": 1,
            "kind": "x = y",
            "value": 0.0,
            "width": 2.0,
            "dash": "solid",
            "color": "#ef4444",
        }
    )
    vert_label = _format_reference_line_label(
        {
            "id": 2,
            "kind": "x = constant",
            "value": 3.14,
            "width": 1.5,
            "dash": "dashed",
            "color": "#ef4444",
        }
    )
    hori_label = _format_reference_line_label(
        {
            "id": 3,
            "kind": "y = constant",
            "value": -2.5,
            "width": 1.0,
            "dash": "dotted",
            "color": "#ef4444",
        }
    )

    assert "#1 x = y" in diag_label
    assert "#2 x = 3.14" in vert_label
    assert "#3 y = -2.5" in hori_label


def test_build_reference_line_overlay_skips_out_of_range_lines() -> None:
    overlay = _build_reference_line_overlay(
        x_min=0.0,
        x_max=10.0,
        y_min=0.0,
        y_max=5.0,
        reference_lines=[
            {
                "id": 1,
                "kind": "x = constant",
                "value": 4.0,
                "width": 2.0,
                "dash": "solid",
                "color": "#ef4444",
            },
            {
                "id": 2,
                "kind": "y = constant",
                "value": 100.0,
                "width": 2.0,
                "dash": "dashed",
                "color": "#ef4444",
            },
            {
                "id": 3,
                "kind": "x = y",
                "value": 0.0,
                "width": 1.0,
                "dash": "dotdash",
                "color": "#ef4444",
            },
        ],
    )

    assert isinstance(overlay, hv.Overlay)
    assert len(overlay) == 2


def test_build_reference_line_overlay_returns_none_when_no_line_visible() -> None:
    overlay = _build_reference_line_overlay(
        x_min=0.0,
        x_max=1.0,
        y_min=0.0,
        y_max=1.0,
        reference_lines=[
            {
                "id": 1,
                "kind": "x = constant",
                "value": 2.0,
                "width": 1.0,
                "dash": "solid",
                "color": "#ef4444",
            },
            {
                "id": 2,
                "kind": "y = constant",
                "value": -1.0,
                "width": 1.0,
                "dash": "solid",
                "color": "#ef4444",
            },
        ],
    )

    assert overlay is None
