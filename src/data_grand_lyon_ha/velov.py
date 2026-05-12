"""Pure filtering functions for Vélo'v station data."""

from .models import VelovStation


def find_velov_station_by_id(
    stations: list[VelovStation], station_id: int
) -> VelovStation | None:
    """Find a station by its ID, or return None if not found."""
    for station in stations:
        if station.number == station_id:
            return station
    return None
