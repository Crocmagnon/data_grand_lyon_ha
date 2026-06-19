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


class TclAlertType(StrEnum):
    """Type of a TCL traffic alert."""

    DISRUPTION = "Perturbation"
    INFORMATION = "Information"
    LINE_INFORMATION = "Information ligne"


class TclAlertSeverityType(StrEnum):
    """Severity category of a TCL traffic alert."""

    SIGNIFICANT_DELAYS = "SIGNIFICANT_DELAYS"
    OTHER_EFFECT = "OTHER_EFFECT"


@dataclass(frozen=True)
class TclAlert:
    """A single TCL traffic alert affecting a line.

    Note: ``niveau_severite`` is *lower for more disruptive* alerts
    (20 = disruption, 30 = information, 40 = line information).
    """

    type: TclAlertType
    cause: str
    debut: datetime
    fin: datetime
    mode: str
    ligne_com: str
    ligne_cli: str
    titre: str
    message: str
    last_update_fme: datetime
    n: int
    type_severite: TclAlertSeverityType
    niveau_severite: int
    type_objet: str
    liste_objet: str


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


@dataclass(frozen=True)
class TclLinePictogram:
    """Pictogram filenames for a single TCL line.

    Each field is the file name of an SVG pictogram (not the image itself):
    ``picto_mode`` is the transport mode icon, ``picto_ligne`` the line number
    badge, and ``picto_complet`` the full pictogram (mode + line number).
    """

    code_ligne: str
    picto_mode: str
    picto_ligne: str
    picto_complet: str


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
