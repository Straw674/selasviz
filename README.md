# selasviz

An interactive 2D visualization workbench for Pandas DataFrames, built with [Panel](https://panel.holoviz.org/) and [HoloViews](https://holoviews.org/). It supports scatter, hexbin, and datashader views.

This project is managed with [uv](https://docs.astral.sh/uv/).

## Installation

### 1) Add to a project

With uv:

```bash
uv add selasviz
```

With pip:

```bash
pip install selasviz
```

After installing into your environment, the CLI entry `selasviz` is also available.

### 2) Use as a tool (CLI only)

Use this when you only need the CLI and do not want to add `selasviz` as a project dependency.

Run directly with uvx (no persistent install):

```bash
uvx --from selasviz selasviz --help
```

Install as a global tool with uv:

```bash
uv tool install selasviz
```

Then run:

```bash
selasviz --help
```

## Quick Start

```python
import pandas as pd
from selasviz import launch_explorer

# Load your data
df = pd.read_csv("your_data.csv")

# Launch and serve the explorer
launch_explorer(df, port=5006, show=True)
```

## CLI (FITS)

The CLI currently supports FITS files only for now.

Launch directly from a FITS table file:

```bash
selasviz data.fits
```

Optional arguments:

```bash
selasviz data.fits --title "Data Explorer" --port 5006
```

## Development (uv)

```bash
git clone https://github.com/Straw674/selasviz
cd selasviz
uv sync --extra dev
```

## Release Versioning

This repository uses Semantic Versioning with
[python-semantic-release](https://python-semantic-release.readthedocs.io/).
The next version is inferred from Conventional Commit prefixes:

- `fix:` -> patch bump
- `feat:` -> minor bump
- `feat!:` or `BREAKING CHANGE:` -> major bump

Run locally:

```bash
uv sync --extra dev
uv run semantic-release version
```

The GitHub workflow also runs this automatically on pushes to `main`.

## License

MIT License
