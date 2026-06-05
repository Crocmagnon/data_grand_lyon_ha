# data_grand_lyon_ha

Python library to retrieve data from the [Grand Lyon open data platform](https://data.grandlyon.com).

Intended for use as a [Home Assistant](https://www.home-assistant.io/) integration backend.

## Installation

```bash
pip install data-grand-lyon-ha
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add data-grand-lyon-ha
```

## Usage

```python
import asyncio
import aiohttp
from data_grand_lyon_ha import DataGrandLyonClient, TclPassageType, find_tcl_stop_by_id

async def main():
    async with aiohttp.ClientSession() as session:
        client = DataGrandLyonClient(session)
        # Or with authentication:
        # client = DataGrandLyonClient(session, username="user", password="pass")

        # Passages for a specific line, stop, and type
        passages = await client.get_tcl_passages("A", 30101, TclPassageType.THEORETICAL)
        for p in passages:
            print(f"{p.ligne} → {p.direction} in {p.delai_passage}")

        # All passages for a stop (all lines and types)
        all_passages = await client.get_tcl_stop_passages(30101)
        for p in all_passages:
            print(f"{p.ligne} → {p.direction} in {p.delai_passage} [{p.type}]")

        # All TCL stops, then look one up by ID
        stops = await client.get_tcl_stops()
        stop = find_tcl_stop_by_id(stops, 1041)
        if stop:
            print(f"{stop.nom} ({stop.commune}) — lines: {stop.desserte}")

asyncio.run(main())
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Run tests
uv run pytest

# Build the package
uv build
```

## License

MIT
