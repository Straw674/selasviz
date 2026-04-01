from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from astropy.table import Table

from selasviz import cli


def test_main_missing_file_raises_system_exit() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["does-not-exist.fits"])

    assert exc_info.value.code == 2


def test_main_returns_one_when_fits_read_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fits_file = tmp_path / "sample.fits"
    fits_file.write_bytes(b"dummy")

    def _raise_read_error(_: Path) -> pd.DataFrame:
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "_read_fits_as_dataframe", _raise_read_error)

    rc = cli.main([str(fits_file)])

    assert rc == 1


def test_main_success_reads_and_launches(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fits_file = tmp_path / "sample.fits"
    fits_file.write_bytes(b"dummy")

    expected_df = pd.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
    calls: list[tuple[pd.DataFrame, str, int, bool]] = []

    def _fake_read(path: Path) -> pd.DataFrame:
        assert path == fits_file
        return expected_df

    def _fake_launch(
        df: pd.DataFrame,
        *,
        title: str,
        port: int,
        show: bool,
    ) -> None:
        calls.append((df, title, port, show))

    monkeypatch.setattr(cli, "_read_fits_as_dataframe", _fake_read)
    monkeypatch.setattr(cli, "launch_explorer", _fake_launch)

    rc = cli.main([str(fits_file), "--title", "T", "--port", "6006"])

    assert rc == 0
    assert len(calls) == 1
    called_df, called_title, called_port, called_show = calls[0]
    assert called_df.equals(expected_df)
    assert called_title == "T"
    assert called_port == 6006
    assert called_show is True


def test_read_fits_as_dataframe_keeps_multidimensional_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    table = Table()
    table["x"] = [1.0, 2.0]
    table["vec"] = np.array([[1, 2, 3], [4, 5, 6]])

    class _FakeTable:
        @staticmethod
        def read(path: Path, format: str):
            assert path == Path("mock.fits")
            assert format == "fits"
            return table

    monkeypatch.setattr(cli, "Table", _FakeTable)

    df = cli._read_fits_as_dataframe(Path("mock.fits"))

    assert df["x"].tolist() == [1.0, 2.0]
    assert isinstance(df.loc[0, "vec"], np.ndarray)
    assert np.array_equal(df.loc[0, "vec"], np.array([1, 2, 3]))
    assert np.array_equal(df.loc[1, "vec"], np.array([4, 5, 6]))


def test_read_fits_as_dataframe_allows_tables_with_only_multidimensional_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    table = Table()
    table["vec"] = np.array([[10, 11], [12, 13]])

    class _FakeTable:
        @staticmethod
        def read(path: Path, format: str):
            assert path == Path("mock_nd_only.fits")
            assert format == "fits"
            return table

    monkeypatch.setattr(cli, "Table", _FakeTable)

    df = cli._read_fits_as_dataframe(Path("mock_nd_only.fits"))

    assert list(df.columns) == ["vec"]
    assert np.array_equal(df.loc[0, "vec"], np.array([10, 11]))
    assert np.array_equal(df.loc[1, "vec"], np.array([12, 13]))
