"""Pure filtering functions for Vélo'v station data."""

from .models import VelovStation


def find_velov_stations_by_ids(
    stations: list[VelovStation], station_ids: list[int]
) -> dict[int, VelovStation | None]:
    """Find multiple stations by their IDs in a single pass."""
    result: dict[int, VelovStation | None] = {sid: None for sid in station_ids}
    remaining = set(station_ids)
    for station in stations:
        if station.number in remaining:
            result[station.number] = station
            remaining.discard(station.number)
            if not remaining:
                break
    return result


def find_velov_station_by_id(
    stations: list[VelovStation], station_id: int
) -> VelovStation | None:
    """Find a station by its ID, or return None if not found."""
    for station in stations:
        if station.number == station_id:
            return station
    return None
