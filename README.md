# selas

An interactive 2D visualization workbench for Pandas DataFrames, built with [Panel](https://panel.holoviz.org/) and [HoloViews](https://holoviews.org/). It supports scatter, hexbin, and datashader views.

This project is managed with [uv](https://docs.astral.sh/uv/).

## Installation

Choose one workflow based on how you want to use `selas`.

### 1) Add to a project

With uv:

```bash
uv add selas
```

With pip:

```bash
pip install selas
```

After installing into your environment, the CLI entry `explore` is also available.

### 2) Use as a tool (CLI only)

Use this when you only need the CLI and do not want to add `selas` as a project dependency.

Run directly with uvx (no persistent install):

```bash
uvx --from selas explore --help
```

Install as a global tool with uv:

```bash
uv tool install selas
```

Then run:

```bash
explore --help
```

## Quick Start

```python
import pandas as pd
from selas import launch_explorer

# Load your data
df = pd.read_csv("your_data.csv")

# Launch and serve the explorer
launch_explorer(df, port=5006, show=True)
```

## CLI (FITS)

The CLI currently supports FITS files only for now.

Launch directly from a FITS table file:

```bash
explore data.fits
```

Optional arguments:

```bash
explore data.fits --title "Cluster Explorer" --port 5006
```

## Development (uv)

```bash
git clone https://github.com/Straw674/selas
cd selas
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

Generated changelog:

- [CHANGELOG.md](./CHANGELOG.md)

## License

MIT License
