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


class StationStatus(StrEnum):
    """Operational status of a Vélo'v station."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Availability(StrEnum):
    """Color-coded availability level of a Vélo'v station."""

    GREEN = "Vert"
    ORANGE = "Orange"
    BLUE = "Bleu"
    GREY = "Gris"


@dataclass(frozen=True)
class VelovAvailability:
    """Detailed bike availability at a Vélo'v station."""

    bikes: int
    electrical_bikes: int
    electrical_internal_battery_bikes: int
    electrical_removable_battery_bikes: int
    mechanical_bikes: int
    stands: int
    capacity: int


@dataclass(frozen=True)
class VelovStationStatus:
    """Status of a Vélo'v station."""

    number: int
    name: str
    address: str
    commune: str
    status: StationStatus
    availability: Availability
    lat: float
    lng: float
    bike_stands: int
    available_bikes: int
    available_bike_stands: int
    banking: bool
    last_update: datetime
    total_stands: VelovAvailability
