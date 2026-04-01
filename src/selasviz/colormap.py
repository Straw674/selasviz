"""Configuration constants for interactive scatter plotting."""

from __future__ import annotations

import colorcet as cc

# Values: list of hex colors (colorcet) or a string name (Bokeh/matplotlib).
_CMAP_OPTIONS: dict[str, list[str] | str] = {
    "Fire": cc.palette["fire"],
    "Blues": cc.palette["blues"],
    "BMY": cc.palette["bmy"],
    "BMW": cc.palette["bmw"],
    "BGYW": cc.palette["bgyw"],
    "Gray": cc.palette["gray"],
    "KBC": cc.palette["kbc"],
    "KGY": cc.palette["kgy"],
    "KB": cc.palette["kb"],
    "Gouldian": cc.palette["gouldian"],
    "Rainbow (cc)": cc.palette["rainbow"],
    "Viridis": "Viridis",
    "Plasma": "Plasma",
    "Inferno": "Inferno",
    "Magma": "Magma",
    "Cividis": "Cividis",
    "Twilight": "twilight",
    "Coolwarm": cc.palette["coolwarm"],
    "CWR (B-W-R)": cc.palette["cwr"],
    "BKR (B-Blk-R)": cc.palette["bkr"],
    "BWG": cc.palette["bwy"],
    "Hot": "hot",
    "Turbo": "turbo",
}
