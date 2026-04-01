from __future__ import annotations

import numpy as np
import pandas as pd

from selasviz.data import (
    filter_outliers,
    sample_large_data,
    select_color_candidate_columns,
    select_scalar_numeric_columns,
)


def test_select_scalar_numeric_columns_filters_expected_dtypes() -> None:
    df = pd.DataFrame(
        {
            "int_col": [1, 2, 3],
            "float_col": [1.0, 2.0, 3.0],
            "bool_col": [True, False, True],
            "str_col": ["a", "b", "c"],
        }
    )

    cols = select_scalar_numeric_columns(df)

    assert cols == ["int_col", "float_col", "bool_col"]


def test_select_color_candidate_columns_keeps_low_cardinality_scalars() -> None:
    df = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "label": ["A", "A", "B", "B"],
            "array_like": [[1], [2], [3], [4]],
            "many_unique": [f"id_{idx}" for idx in range(4)],
        }
    )

    cols = select_color_candidate_columns(df, max_categorical_unique=3)

    assert "x" in cols
    assert "label" in cols
    assert "array_like" not in cols
    assert "many_unique" not in cols


def test_sample_large_data_returns_original_when_sampling_disabled() -> None:
    df = pd.DataFrame({"x": np.arange(1000), "y": np.arange(1000)})

    out = sample_large_data(df, "x", "y", target_size=100, sample_size=None)

    assert out is df


def test_sample_large_data_downsamples_and_cleans_helper_columns() -> None:
    rng = np.random.default_rng(7)
    n_rows = 5000
    df = pd.DataFrame(
        {
            "x": rng.normal(0, 1, n_rows),
            "y": rng.normal(0, 1, n_rows),
            "value": rng.integers(0, 10, n_rows),
        }
    )

    out = sample_large_data(df, "x", "y", target_size=1000, sample_size=500)

    assert len(out) <= 500
    assert set(out.columns) == {"x", "y", "value"}


def test_filter_outliers_removes_invalid_values() -> None:
    df = pd.DataFrame(
        {
            "x": [1.0, np.nan, np.inf, 2.0, 3.0],
            "y": [1.0, 2.0, 3.0, -np.inf, 4.0],
        }
    )

    out = filter_outliers(df, "x", "y", clip_pct=0.0)

    assert len(out) == 2
    assert out["x"].tolist() == [1.0, 3.0]


def test_filter_outliers_clip_percentile_removes_extreme_point() -> None:
    df = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 1000.0],
            "y": [1.0, 2.0, 3.0, 4.0, 1000.0],
        }
    )

    out = filter_outliers(df, "x", "y", clip_pct=10.0)

    assert out["x"].max() < 1000.0
    assert out["y"].max() < 1000.0
