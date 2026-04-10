"""Data models for TCL/Sytral transport data."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PassageType(StrEnum):
    """Type of passage: theoretical or estimated."""

    THEORETICAL = "T"
    ESTIMATED = "E"


@dataclass(frozen=True)
class Passage:
    """A single passage of a bus/tram/metro at a stop."""

    id: int
    ligne: str
    direction: str
    delai_passage: str
    type: PassageType
    heure_passage: datetime
    id_tarret_destination: int
    course_theorique: str
