"""Standalone demo script for selasviz.

This script is intentionally outside the package module tree so it can be
executed directly without relying on package-relative imports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running from a source checkout without installation.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from selasviz import launch_explorer


def build_demo_dataframe(rows: int, seed: int) -> pd.DataFrame:
    """Generate a synthetic catalog-like DataFrame for local demo use."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "ra": rng.uniform(200, 220, rows),
            "dec": rng.uniform(40, 50, rows),
            "redshift": rng.uniform(0.05, 0.8, rows),
            "mass": 10 ** rng.uniform(13, 15, rows),
            "richness": rng.integers(10, 200, rows),
            "name": [f"CLJ{i:05d}" for i in range(rows)],
        }
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run selasviz demo with fake data")
    parser.add_argument("--rows", type=int, default=50000, help="Number of rows")
    parser.add_argument("--seed", type=int, default=27, help="Random seed")
    parser.add_argument("--title", default="Demo Explorer", help="Dashboard title")
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Server port for Panel (0 picks a free port)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    demo_df = build_demo_dataframe(rows=args.rows, seed=args.seed)
    launch_explorer(demo_df, title=args.title, port=args.port, show=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
