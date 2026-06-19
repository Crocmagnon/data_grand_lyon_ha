"""Data models for the Grand Lyon open data platform."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TclPassageType(StrEnum):
    """Type of passage: theoretical or estimated."""

    THEORETICAL = "T"
    ESTIMATED = "E"


@dataclass(frozen=True)
class TclPassage:
    """A single passage of a bus/tram/metro at a stop."""

    id: int
    ligne: str
    direction: str
    delai_passage: str
    type: TclPassageType
    heure_passage: datetime
    id_tarret_destination: int
    course_theorique: str


@dataclass(frozen=True)
class TclStop:
    """A single transit network stop."""
    id: int
    gid: int
    adresse: str
    ascenseur: bool
    commune: str
    desserte: list[str]
    escalator: bool
    insee: str
    last_update: datetime | None
    lat: float
    lon: float
    nom: str
    pmr: bool


@dataclass(frozen=True)
class TclParkAndRide:
    """A single TCL park-and-ride (P+R) facility with real-time availability."""

    id: str
    gid: int
    nom: str
    capacite: int
    place_handi: int
    horaires: str
    p_surv: bool
    nb_tot_place_dispo: int
    last_update: datetime | None
    last_update_fme: datetime | None


class VelovStationStatus(StrEnum):
    """Operational status of a Vélo'v station."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class VelovAvailabilityLevel(StrEnum):
    """Color-coded availability level of a Vélo'v station."""

    GREEN = "Vert"
    ORANGE = "Orange"
    BLUE = "Bleu"
    GREY = "Gris"


@dataclass(frozen=True)
class VelovBikeStandAvailability:
    """Detailed bike availability at a Vélo'v station."""

    bikes: int
    electrical_bikes: int
    electrical_internal_battery_bikes: int
    electrical_removable_battery_bikes: int
    mechanical_bikes: int
    stands: int
    capacity: int


@dataclass(frozen=True)
class VelovStation:
    """Status of a Vélo'v station."""

    number: int
    name: str
    address: str
    commune: str
    status: VelovStationStatus
    availability: VelovAvailabilityLevel
    lat: float
    lng: float
    bike_stands: int
    available_bikes: int
    available_bike_stands: int
    banking: bool
    last_update: datetime | None
    total_stands: VelovBikeStandAvailability
