"""Data preparation helpers for interactive scatter plotting."""

from __future__ import annotations

import numpy as np
import pandas as pd


def select_scalar_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return scalar numeric columns usable for plotting axes.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe.

    Returns
    -------
    list[str]
        Column names with dtype kind in ``iufb``.
    """
    scalar_mask = df.dtypes.apply(lambda dtype: dtype.kind in "iufb")
    return scalar_mask[scalar_mask].index.tolist()


def select_color_candidate_columns(
    df: pd.DataFrame,
    max_categorical_unique: int = 50,
) -> list[str]:
    """Return columns that can be used for scatter color encoding.

    Numeric scalar columns are always allowed. Non-numeric columns are also
    included when they have low cardinality and behave like scalar categories
    (for example ``str``, ``bytes``, ``datetime``, enums, or other hashable
    scalar values).

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe.
    max_categorical_unique : int
        Maximum unique non-null categories for string/categorical columns.

    Returns
    -------
    list[str]
        Candidate columns for the ``Color column`` selector.
    """

    def _is_scalar_like_object(series: pd.Series) -> bool:
        non_null = series.dropna()
        if non_null.empty:
            return False
        return bool(
            non_null.map(
                lambda value: (
                    not isinstance(
                        value,
                        (list, tuple, dict, set, np.ndarray),
                    )
                )
            ).all()
        )

    color_cols = select_scalar_numeric_columns(df)

    for col in df.columns:
        if col in color_cols:
            continue

        series = df[col]
        if isinstance(series.dtype, pd.CategoricalDtype):
            unique_count = int(series.nunique(dropna=True))
            if unique_count < 1 or unique_count > max_categorical_unique:
                continue
            color_cols.append(col)
            continue

        if pd.api.types.is_datetime64_any_dtype(series):
            unique_count = int(series.nunique(dropna=True))
            if unique_count < 1 or unique_count > max_categorical_unique:
                continue
            color_cols.append(col)
            continue

        if pd.api.types.is_object_dtype(series):
            non_null = series.dropna()
            if non_null.empty:
                continue

            if not _is_scalar_like_object(series):
                continue

        try:
            unique_count = int(series.nunique(dropna=True))
        except TypeError:
            continue

        if unique_count < 1 or unique_count > max_categorical_unique:
            continue

        if pd.api.types.is_object_dtype(series):
            color_cols.append(col)
            continue

        if pd.api.types.is_string_dtype(series):
            color_cols.append(col)

    return color_cols


def sample_large_data(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    target_size: int = 100000,
    sample_size: int | None = None,
) -> pd.DataFrame:
    """Sample large datasets while preserving visual distribution.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    target_size : int
        Threshold above which sampling can be applied.
    sample_size : int | None
        Target sample size. If ``None``, no sampling is applied.

    Returns
    -------
    pd.DataFrame
        Original or sampled dataframe.
    """
    if sample_size is None or len(df) <= target_size:
        return df

    if sample_size >= len(df):
        return df

    n_bins = int(np.sqrt(sample_size / 100))
    n_bins = max(5, min(100, n_bins))

    x_min, x_max = df[x_col].min(), df[x_col].max()
    y_min, y_max = df[y_col].min(), df[y_col].max()

    x_eps = (x_max - x_min) * 1e-6 + 1e-10
    y_eps = (y_max - y_min) * 1e-6 + 1e-10
    x_max += x_eps
    y_max += y_eps

    sampled = df.copy()
    sampled["_x_bin"] = pd.cut(sampled[x_col], bins=n_bins, labels=False)
    sampled["_y_bin"] = pd.cut(sampled[y_col], bins=n_bins, labels=False)

    samples_per_bin = max(1, sample_size // (n_bins * n_bins))
    sampled_list: list[pd.DataFrame] = []
    for _, group in sampled.groupby(["_x_bin", "_y_bin"], observed=True):
        sample_n = min(len(group), samples_per_bin)
        sampled_list.append(group.sample(n=sample_n, random_state=42))

    result = pd.concat(sampled_list, ignore_index=True)
    result = result.drop(columns=["_x_bin", "_y_bin"]).head(sample_size)
    return result.reset_index(drop=True)


def filter_outliers(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    clip_pct: float,
) -> pd.DataFrame:
    """Filter NaN/Inf and optional percentile-based outliers on X and Y.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe.
    x_col : str
        X-axis column name.
    y_col : str
        Y-axis column name.
    clip_pct : float
        Percentile clip amount for both tails.

    Returns
    -------
    pd.DataFrame
        Filtered dataframe.
    """
    valid_mask = (
        pd.notna(df[x_col])
        & (df[x_col] != np.inf)
        & (df[x_col] != -np.inf)
        & pd.notna(df[y_col])
        & (df[y_col] != np.inf)
        & (df[y_col] != -np.inf)
    )
    valid_df = df[valid_mask]

    if valid_df.empty or clip_pct <= 0:
        return valid_df

    if df[x_col].dtype == bool or df[y_col].dtype == bool:
        return valid_df

    x_min = valid_df[x_col].quantile(clip_pct / 100.0)
    x_max = valid_df[x_col].quantile(1 - (clip_pct / 100.0))
    y_min = valid_df[y_col].quantile(clip_pct / 100.0)
    y_max = valid_df[y_col].quantile(1 - (clip_pct / 100.0))

    mask = (
        (valid_df[x_col] >= x_min)
        & (valid_df[x_col] <= x_max)
        & (valid_df[y_col] >= y_min)
        & (valid_df[y_col] <= y_max)
    )
    return valid_df[mask]
