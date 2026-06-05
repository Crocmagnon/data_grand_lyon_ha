"""HTTP client for the Grand Lyon open data API."""

from datetime import datetime

import aiohttp

from .models import (
    TclPassage,
    TclPassageType,
    TclStop,
    VelovAvailabilityLevel,
    VelovBikeStandAvailability,
    VelovStation,
    VelovStationStatus,
)

_PASSAGE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _parse_tcl_desserte(desserte: str) -> list[str]:
    res = []
    for d in desserte.split(","):
        res.append(d.split(":")[0])
    return res


class DataGrandLyonClient:
    """HTTP client for the Grand Lyon open data API."""

    BASE_URL = "https://data.grandlyon.com/fr/datapusher/ws/rdata"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._session = session
        self._auth: aiohttp.BasicAuth | None = None
        if username is not None and password is not None:
            self._auth = aiohttp.BasicAuth(username, password)

    async def get_tcl_passages(self) -> list[TclPassage]:
        """Retrieve all TCL passages from the API."""
        url = f"{self.BASE_URL}/tcl_sytral.tclpassagearret/all.json"
        async with self._session.get(
            url, params={"maxfeatures": "-1"}, auth=self._auth
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        return [
            TclPassage(
                id=v["id"],
                ligne=v["ligne"],
                direction=v["direction"],
                delai_passage=v["delaipassage"],
                type=TclPassageType(v["type"]),
                heure_passage=datetime.strptime(
                    v["heurepassage"], _PASSAGE_DATETIME_FORMAT
                ),
                id_tarret_destination=v["idtarretdestination"],
                course_theorique=v["coursetheorique"],
            )
            for v in data["values"]
        ]

    async def get_tcl_stops(self) -> list[TclStop]:
        """Retrieve all TCL stops from the API."""
        url = f"{self.BASE_URL}/tcl_sytral.tclarret/all.json"
        async with self._session.get(
            url, params={"maxfeatures": "-1"}, auth=self._auth
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        return [
            TclStop(
                id=v["id"],
                gid=v["gid"],
                adresse=v["adresse"],
                ascenseur=v["ascenseur"],
                commune=v["commune"],
                escalator=v["escalator"],
                insee=v["insee"],
                last_update=datetime.fromisoformat(v["last_update"]) if v["last_update"] else None,
                lat=v["lat"],
                lon=v["lon"],
                nom=v["nom"],
                pmr=v["pmr"],
                desserte=_parse_tcl_desserte(v["desserte"]),
            )
            for v in data["values"]
        ]

    async def get_velov_stations(self) -> list[VelovStation]:
        """Retrieve all Vélo'v stations from the API."""
        url = f"{self.BASE_URL}/jcd_jcdecaux.jcdvelov/all.json"
        async with self._session.get(
            url, params={"maxfeatures": "-1"}
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        stations = []
        for v in data["values"]:
            ts = v["total_stands"]
            stations.append(
                VelovStation(
                    number=v["number"],
                    name=v["name"],
                    address=v["address"],
                    commune=v["commune"],
                    status=VelovStationStatus(v["status"]),
                    availability=VelovAvailabilityLevel(v["availability"]),
                    lat=v["lat"],
                    lng=v["lng"],
                    bike_stands=v["bike_stands"],
                    available_bikes=v["available_bikes"],
                    available_bike_stands=v["available_bike_stands"],
                    banking=v["banking"],
                    last_update=datetime.fromisoformat(v["last_update"]) if v["last_update"] else None,
                    total_stands=VelovBikeStandAvailability(
                        bikes=ts["availabilities"]["bikes"],
                        electrical_bikes=ts["availabilities"]["electricalBikes"],
                        electrical_internal_battery_bikes=ts["availabilities"][
                            "electricalInternalBatteryBikes"
                        ],
                        electrical_removable_battery_bikes=ts["availabilities"][
                            "electricalRemovableBatteryBikes"
                        ],
                        mechanical_bikes=ts["availabilities"]["mechanicalBikes"],
                        stands=ts["availabilities"]["stands"],
                        capacity=ts["capacity"],
                    ),
                )
            )
        return stations
