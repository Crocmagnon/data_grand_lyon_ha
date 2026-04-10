"""HTTP client for the Grand Lyon TCL/Sytral data API."""

from datetime import datetime

import aiohttp

from .models import Passage, PassageType

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
        passage_type: PassageType,
    ) -> list[Passage]:
        """Retrieve passages for a given line, stop, and passage type."""
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
            and v["type"] == passage_type
        ]
        passages.sort(key=lambda p: p.heure_passage)
        return passages
