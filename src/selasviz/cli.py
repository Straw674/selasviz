"""Command-line entry for launching selasviz from a FITS table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from astropy.table import Table

from .explorer import launch_explorer


def _read_fits_as_dataframe(path: Path):
    """Read a FITS table into a pandas DataFrame."""
    table = Table.read(path, format="fits")

    # Split columns into scalar/1D and multidimensional groups.
    cols_1d = [name for name in table.colnames if len(table[name].shape) <= 1]
    cols_nd = [name for name in table.colnames if len(table[name].shape) > 1]

    # Use astropy's conversion for 1D columns; it preserves dtype/mask behavior.
    if cols_1d:
        df = table[cols_1d].to_pandas()
    else:
        df = pd.DataFrame(index=range(len(table)))

    # Store multidimensional cells as per-row array objects.
    for name in cols_nd:
        df[name] = list(table[name])

    return df


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="selasviz",
        description="Launch selasviz with a FITS table file.",
    )
    parser.add_argument("fits_file", type=Path, help="Path to FITS table file")
    parser.add_argument("--title", default="Selasviz Explorer", help="Dashboard title")
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Server port for Panel (0 picks a free port)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.fits_file.exists() or not args.fits_file.is_file():
        parser.error(f"FITS file not found: {args.fits_file}")

    try:
        df = _read_fits_as_dataframe(args.fits_file)
    except Exception as exc:  # pragma: no cover - runtime I/O path
        print(f"Failed to read FITS file '{args.fits_file}': {exc}", file=sys.stderr)
        return 1

    launch_explorer(df, title=args.title, port=args.port, show=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
