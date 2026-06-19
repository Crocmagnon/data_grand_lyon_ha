"""Pure filtering and sorting functions for TCL passage data."""

from .models import TclParkAndRide, TclPassage, TclStop


def filter_tcl_passages_by_line(
    passages: list[TclPassage], ligne: str
) -> list[TclPassage]:
    """Keep only passages for a given line."""
    return [p for p in passages if p.ligne == ligne]


def filter_tcl_passages_by_stop(
    passages: list[TclPassage], stop_id: int
) -> list[TclPassage]:
    """Keep only passages for a given stop ID."""
    return [p for p in passages if p.id == stop_id]


def find_tcl_stop_by_id(
    stops: list[TclStop], stop_id: int
) -> TclStop | None:
    """Find a stop by its ID, or return None if not found."""
    for stop in stops:
        if stop.id == stop_id:
            return stop
    return None


def find_tcl_park_and_ride_by_id(
    parks: list[TclParkAndRide], park_id: str
) -> TclParkAndRide | None:
    """Find a park-and-ride by its ID, or return None if not found."""
    for park in parks:
        if park.id == park_id:
            return park
    return None


def filter_tcl_passages_by_lines_stops(
    passages: list[TclPassage], lines_stops: list[tuple[str, int]]
) -> dict[tuple[str, int], list[TclPassage]]:
    """Group passages by (line, stop_id) pairs, keeping only matching passages."""
    result: dict[tuple[str, int], list[TclPassage]] = {key: [] for key in lines_stops}
    keys = set(lines_stops)
    for p in passages:
        key = (p.ligne, p.id)
        if key in keys:
            result[key].append(p)
    return result


def sort_tcl_passages_by_time(
    passages: list[TclPassage],
) -> list[TclPassage]:
    """Sort passages by heure_passage ascending."""
    return sorted(passages, key=lambda p: p.heure_passage)
