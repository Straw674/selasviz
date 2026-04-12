from __future__ import annotations

import panel as pn
import pytest

from selasviz.colormap import _CMAP_OPTIONS
from selasviz.ui import (
    _compute_auto_best_plot_size,
    create_dashboard,
    create_sidebar,
    create_widgets,
)


def test_create_widgets_defaults_to_square_plot_size_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("selasviz.ui._detect_display_resolution", lambda: (2560, 1440))
    widgets = create_widgets(["x", "y"], ["color"], 10, _CMAP_OPTIONS)

    assert widgets["plot_size_lock"].value is True
    assert widgets["plot_size_lock"].name == "Keep 1:1 plot body ratio"
    assert widgets["width"].value == widgets["height"].value == 1200


def test_create_widgets_syncs_plot_dimensions_when_locked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("selasviz.ui._detect_display_resolution", lambda: (2560, 1440))
    widgets = create_widgets(["x", "y"], ["color"], 10, _CMAP_OPTIONS)

    widgets["width"].value = 1450
    assert widgets["height"].value == 1450

    widgets["height"].value = 900
    assert widgets["width"].value == 900


def test_create_widgets_allows_independent_dimensions_when_unlocked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("selasviz.ui._detect_display_resolution", lambda: (2560, 1440))
    widgets = create_widgets(["x", "y"], ["color"], 10, _CMAP_OPTIONS)

    widgets["plot_size_lock"].value = False
    widgets["width"].value = 1500

    assert widgets["height"].value == 1200

    widgets["height"].value = 1100
    assert widgets["width"].value == 1500


def test_create_dashboard_plot_panel_does_not_override_width() -> None:
    sidebar = pn.Column("sidebar")
    dashboard = create_dashboard("T", sidebar, pn.pane.Markdown("plot"))

    layout = dashboard[1]
    plot_column = layout[1]
    plot_panel = plot_column[0]

    assert plot_panel.sizing_mode is None


def test_compute_auto_best_plot_size() -> None:
    assert _compute_auto_best_plot_size(2560, 1440) == 1200
    assert _compute_auto_best_plot_size(1366, 768) == 500


def test_create_sidebar_shows_detected_display_and_auto_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("selasviz.ui._detect_display_resolution", lambda: (1920, 1080))
    widgets = create_widgets(["x", "y"], ["color"], 10, _CMAP_OPTIONS)
    controls = {
        "scatter_controls": pn.Column("scatter"),
        "hexbin_controls": pn.Column("hexbin"),
        "ds_controls": pn.Column("ds"),
    }

    sidebar = create_sidebar(widgets, controls, n_rows=10)
    display_info = widgets["display_info"].object

    assert "Adaptive size/Detected display:" in display_info
    assert "800x800" in display_info
    assert "1920x1080" in display_info
    assert widgets["display_info"] in sidebar
    assert not hasattr(widgets, "best_size_info") or widgets.get("best_size_info") is None