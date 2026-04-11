# CLAUDE.md

## Project Overview

Python library to retrieve public transport data from the TCL/Sytral network in Lyon, France.
Intended for use as a Home Assistant integration backend.

Uses `aiohttp` with session injection (the caller provides an `aiohttp.ClientSession`), following the standard Home Assistant integration pattern.

## Development Commands

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_client.py::test_client_without_credentials

# Build the package
uv build

# Run the playground script (manual testing against live API)
uv run python contrib/playground.py

# With credentials
TCL_USERNAME=xxx TCL_PASSWORD=yyy uv run python contrib/playground.py
```

## Architecture

- **src layout**: Source code lives in `src/data_grand_lyon_ha/`
- **Build backend**: hatchling
- **Package manager**: uv
- **CI/CD**: Forgejo Actions (`.forgejo/workflows/ci.yml`)
  - Tests run on every push to main and on PRs
  - Publishing to PyPI happens on `v*` tag push

### Key Modules

- `client.py` — `DataGrandLyonClient` class: async HTTP client for the Grand Lyon data API (`https://data.grandlyon.com/fr/datapusher/ws/rdata`)
- `models.py` — Data models: `Passage`, `PassageType`, `VelovStationStatus`, `VelovAvailability`, `StationStatus`, `Availability`

## Conventions

- Type annotations on all public functions
- Docstrings on all public modules and functions
- Tests in `tests/` directory, using pytest + pytest-asyncio

## Checklist for New Features

When adding or modifying features, make sure to update:

1. **Tests** — add or update tests in `tests/`
2. **Documentation** — update `README.md` usage examples if the public API changes
3. **CLAUDE.md** — update this file if architecture, modules, or conventions change
4. **Playground** — update `contrib/playground.py` to exercise new methods
