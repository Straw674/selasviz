from __future__ import annotations

import pandas as pd

from selasviz.scatter_renderer import (
    _normalize_category_value,
    get_discrete_colormap,
    is_categorical_column,
    resolve_color_mapping_mode,
)


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
