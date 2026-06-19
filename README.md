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
from data_grand_lyon_ha import (
    DataGrandLyonClient,
    filter_tcl_passages_by_line,
    filter_tcl_passages_by_stop,
    find_tcl_park_and_ride_by_id,
    find_tcl_stop_by_id,
    find_velov_station_by_id,
    sort_tcl_passages_by_time,
)

async def main():
    async with aiohttp.ClientSession() as session:
        client = DataGrandLyonClient(session)
        # Or with authentication (required for real-time TCL passages):
        # client = DataGrandLyonClient(session, username="user", password="pass")

        # TCL passages: fetch all, then filter and sort client-side
        all_passages = await client.get_tcl_passages()
        passages = filter_tcl_passages_by_stop(
            filter_tcl_passages_by_line(all_passages, "A"), 30101
        )
        for p in sort_tcl_passages_by_time(passages):
            print(f"{p.ligne} → {p.direction} in {p.delai_passage} [{p.type}]")

        # TCL stops: fetch all, then look one up by ID
        stops = await client.get_tcl_stops()
        stop = find_tcl_stop_by_id(stops, 1041)
        if stop:
            print(f"{stop.nom} ({stop.commune}) — lines: {stop.desserte}")

        # Vélo'v stations: fetch all, then look one up by ID
        stations = await client.get_velov_stations()
        station = find_velov_station_by_id(stations, 10044)
        if station:
            print(
                f"{station.name}: {station.available_bikes}/{station.bike_stands} bikes"
            )

        # TCL park-and-rides (P+R): fetch all, then look one up by ID
        parks = await client.get_tcl_park_and_rides()
        park = find_tcl_park_and_ride_by_id(parks, "VAI2")
        if park:
            print(
                f"{park.nom}: {park.nb_tot_place_dispo}/{park.capacite} places"
            )

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
