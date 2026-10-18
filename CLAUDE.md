# CLAUDE.md

## Project Overview

Python library to retrieve open data from the Grand Lyon platform: TCL/Sytral public transport (stops and real-time passages) and Vélo'v bike-sharing stations.
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
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yml`), publishing to PyPI with trusted publishing
  - Tests run on every push to main and on PRs
  - Publishing to PyPI happens on `v*` tag push

### Key Modules

- `client.py` — `DataGrandLyonClient` class: async HTTP client for the Grand Lyon data API (`https://data.grandlyon.com/fr/datapusher/ws/rdata`)
- `models.py` — Data models: `TclPassage`, `TclPassageType`, `TclStop`, `TclParkAndRide`, `TclLinePictogram`, `TclAlert`, `TclAlertType`, `TclAlertSeverityType`, `VelovStation`, `VelovStationStatus`, `VelovAvailabilityLevel`, `VelovBikeStandAvailability`
- `tcl.py` — Pure helpers for TCL data: `filter_tcl_passages_by_line`, `filter_tcl_passages_by_stop`, `filter_tcl_passages_by_lines_stops`, `find_tcl_stop_by_id`, `find_tcl_park_and_ride_by_id`, `find_tcl_line_pictogram_by_code`, `extract_tcl_pictogram_from_zip`, `sort_tcl_passages_by_time`, and for alerts `filter_tcl_alerts_by_line`, `filter_tcl_active_alerts`, `tcl_alert_relevance`/`TclAlertRelevance`, `sort_tcl_alerts_by_relevance`
- `velov.py` — Pure helpers for Vélo'v data: `find_velov_station_by_id`, `find_velov_stations_by_ids`

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
