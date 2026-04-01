"""Command-line entry for launching selasviz from a FITS table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from astropy.table import Table

from .explorer import launch_explorer


def _read_fits_as_dataframe(path: Path):
    """Read a FITS table into a pandas DataFrame."""
    table = Table.read(path, format="fits")
    return table.to_pandas()


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
