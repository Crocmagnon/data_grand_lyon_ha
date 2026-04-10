"""HTTP client for the Grand Lyon TCL/Sytral data API."""

from datetime import datetime

import aiohttp

from .models import (
    Availability,
    Passage,
    PassageType,
    StationStatus,
    VelovAvailability,
    VelovStationStatus,
)

_PASSAGE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TCLClient:
    """HTTP client for the Grand Lyon TCL/Sytral data API."""

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

    async def get_passages(
        self,
        ligne: str,
        stop_id: int,
        passage_type: PassageType | None = None,
    ) -> list[Passage]:
        """Retrieve passages for a given line and stop, optionally filtered by type."""
        url = f"{self.BASE_URL}/tcl_sytral.tclpassagearret/all.json"
        async with self._session.get(
            url, params={"maxfeatures": "-1"}, auth=self._auth
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        passages = [
            Passage(
                id=v["id"],
                ligne=v["ligne"],
                direction=v["direction"],
                delai_passage=v["delaipassage"],
                type=PassageType(v["type"]),
                heure_passage=datetime.strptime(
                    v["heurepassage"], _PASSAGE_DATETIME_FORMAT
                ),
                id_tarret_destination=v["idtarretdestination"],
                course_theorique=v["coursetheorique"],
            )
            for v in data["values"]
            if v["ligne"] == ligne
            and v["id"] == stop_id
            and (passage_type is None or v["type"] == passage_type)
        ]
        passages.sort(key=lambda p: p.heure_passage)
        return passages

    async def get_stop_passages(
        self,
        stop_id: int,
    ) -> list[Passage]:
        """Retrieve all passages for a given stop, regardless of line or type."""
        url = f"{self.BASE_URL}/tcl_sytral.tclpassagearret/all.json"
        async with self._session.get(
            url, params={"maxfeatures": "-1"}, auth=self._auth
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        passages = [
            Passage(
                id=v["id"],
                ligne=v["ligne"],
                direction=v["direction"],
                delai_passage=v["delaipassage"],
                type=PassageType(v["type"]),
                heure_passage=datetime.strptime(
                    v["heurepassage"], _PASSAGE_DATETIME_FORMAT
                ),
                id_tarret_destination=v["idtarretdestination"],
                course_theorique=v["coursetheorique"],
            )
            for v in data["values"]
            if v["id"] == stop_id
        ]
        passages.sort(key=lambda p: p.heure_passage)
        return passages

    async def get_velov_station(
        self, station_id: int
    ) -> VelovStationStatus | None:
        """Retrieve the status of a Vélo'v station by its ID."""
        url = f"{self.BASE_URL}/jcd_jcdecaux.jcdvelov/all.json"
        async with self._session.get(
            url, params={"maxfeatures": "-1", "start": "1"}
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

        for v in data["values"]:
            if v["number"] == station_id:
                ts = v["total_stands"]
                return VelovStationStatus(
                    number=v["number"],
                    name=v["name"],
                    address=v["address"],
                    commune=v["commune"],
                    status=StationStatus(v["status"]),
                    availability=Availability(v["availability"]),
                    lat=v["lat"],
                    lng=v["lng"],
                    bike_stands=v["bike_stands"],
                    available_bikes=v["available_bikes"],
                    available_bike_stands=v["available_bike_stands"],
                    banking=v["banking"],
                    last_update=datetime.fromisoformat(v["last_update"]),
                    total_stands=VelovAvailability(
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
        return None
