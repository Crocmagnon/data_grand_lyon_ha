"""Pure filtering and sorting functions for TCL passage data."""

import io
import zipfile
from datetime import datetime
from enum import IntEnum

from .models import TclAlert, TclLinePictogram, TclParkAndRide, TclPassage, TclStop


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


def find_tcl_stop_by_id(stops: list[TclStop], stop_id: int) -> TclStop | None:
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


def find_tcl_line_pictogram_by_code(
    lines: list[TclLinePictogram], code: str
) -> TclLinePictogram | None:
    """Find a line pictogram entry by its line code, or return None if not found."""
    for line in lines:
        if line.code_ligne == code:
            return line
    return None


def extract_tcl_pictogram_from_zip(zip_bytes: bytes, filename: str) -> bytes | None:
    """Extract a single pictogram SVG from the pictograms ZIP archive.

    Returns the file's raw bytes (suitable for Home Assistant image entities),
    or None if the archive does not contain ``filename``.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        try:
            return archive.read(filename)
        except KeyError:
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


class TclAlertRelevance(IntEnum):
    """Relevance bucket of a TCL alert relative to a reference time.

    Lower is more relevant, so it can be used directly as a sort key.
    """

    CURRENT = 0  # ongoing, or starting today (even if not started yet)
    UPCOMING = 1  # starts on a later day
    ENDED = 2  # already finished


def tcl_alert_relevance(alert: TclAlert, now: datetime) -> TclAlertRelevance:
    """Classify an alert by relevance relative to ``now`` (naive, local time)."""
    if alert.fin < now:
        return TclAlertRelevance.ENDED
    if alert.debut <= now or alert.debut.date() == now.date():
        return TclAlertRelevance.CURRENT
    return TclAlertRelevance.UPCOMING


def filter_tcl_alerts_by_line(alerts: list[TclAlert], ligne: str) -> list[TclAlert]:
    """Keep only alerts for a given line (matched on its user-facing label)."""
    return [a for a in alerts if a.ligne_cli == ligne]


def filter_tcl_active_alerts(alerts: list[TclAlert], now: datetime) -> list[TclAlert]:
    """Keep only alerts that are not over yet (ongoing or upcoming)."""
    return [a for a in alerts if a.fin >= now]


def sort_tcl_alerts_by_relevance(
    alerts: list[TclAlert], now: datetime
) -> list[TclAlert]:
    """Sort alerts most-relevant-first.

    Order: relevance bucket (current/today, upcoming, ended), then severity
    (``niveau_severite`` ascending = more disruptive first), then start time.
    Ended alerts are kept (placed last), not removed.
    """
    return sorted(
        alerts,
        key=lambda a: (
            tcl_alert_relevance(a, now),
            a.niveau_severite,
            a.debut,
        ),
    )
