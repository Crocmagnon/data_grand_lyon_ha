from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from data_grand_lyon_ha import (
    DataGrandLyonClient,
    TclParkAndRide,
    TclPassage,
    TclPassageType,
    TclStop,
    VelovAvailabilityLevel,
    VelovBikeStandAvailability,
    VelovStation,
    VelovStationStatus,
)
from data_grand_lyon_ha.client import _parse_tcl_desserte

SAMPLE_TCL_RESPONSE = {
    "fields": [],
    "nb_results": 3,
    "values": [
        {
            "id": 30101,
            "ligne": "A",
            "direction": "Vaulx-en-Velin La Soie",
            "delaipassage": "25 min",
            "type": "T",
            "heurepassage": "2026-04-10 16:52:43",
            "idtarretdestination": 36394,
            "coursetheorique": "301_301A-0805V_00701083",
            "gid": 1,
            "last_update_fme": "2026-04-10 16:27:01",
        },
        {
            "id": 30101,
            "ligne": "A",
            "direction": "Vaulx-en-Velin La Soie",
            "delaipassage": "3 min",
            "type": "E",
            "heurepassage": "2026-04-10 16:30:00",
            "idtarretdestination": 36394,
            "coursetheorique": "301_301A-0805V_00701084",
            "gid": 2,
            "last_update_fme": "2026-04-10 16:27:01",
        },
        {
            "id": 99999,
            "ligne": "B",
            "direction": "Charpennes",
            "delaipassage": "10 min",
            "type": "T",
            "heurepassage": "2026-04-10 16:37:00",
            "idtarretdestination": 42575,
            "coursetheorique": "302_302B-0100V_00801001",
            "gid": 3,
            "last_update_fme": "2026-04-10 16:27:01",
        },
    ],
}

SAMPLE_TCL_STOPS_RESPONSE = {
    "fields": [],
    "nb_results": 3,
    "values": [
        {
            "id": 1041,
            "gid": 31977,
            "adresse": "111 AVENUE PAUL SANTY",
            "ascenseur": False,
            "commune": "Lyon 8e Arrondissement",
            "desserte": "C25:R",
            "escalator": False,
            "insee": "69388",
            "last_update": "2026-06-05 01:46:00",
            "lat": 45.727741988888,
            "lon": 4.878116954554,
            "nom": "Général André",
            "pmr": True,
        },
        {
            "id": 21844,
            "gid": 37682,
            "adresse": None,
            "ascenseur": None,
            "commune": None,
            "desserte": "JD617:R,JD621:R",
            "escalator": None,
            "insee": None,
            "last_update": None,
            "lat": 45.801439,
            "lon": 4.396345,
            "nom": "Villecheneve Montlit",
            "pmr": False,
        },
        {
            "id": 30202,
            "gid": 40200,
            "adresse": "Rue Exemple",
            "ascenseur": True,
            "commune": "Lyon",
            "desserte": "204:R,215:R,JD473:R",
            "escalator": True,
            "insee": "69123",
            "last_update": "2026-06-05 01:46:00",
            "lat": 45.75,
            "lon": 4.85,
            "nom": "Exemple",
            "pmr": True,
        },
    ],
}

SAMPLE_VELOV_RESPONSE = {
    "fields": [],
    "nb_results": 2,
    "values": [
        {
            "number": 15002,
            "name": "15002 - ST PRIEST - CITE BERLIET",
            "address": "Place Steven Spielberg",
            "commune": "Saint-Priest",
            "status": "OPEN",
            "availability": "Vert",
            "lat": 45.70597,
            "lng": 4.900886,
            "bike_stands": 20,
            "available_bikes": 7,
            "available_bike_stands": 13,
            "banking": False,
            "last_update": "2026-04-10 16:28:08+02:00",
            "total_stands": {
                "availabilities": {
                    "bikes": 7,
                    "electricalBikes": 3,
                    "electricalInternalBatteryBikes": 3,
                    "electricalRemovableBatteryBikes": 0,
                    "mechanicalBikes": 4,
                    "stands": 13,
                },
                "capacity": 20,
            },
        },
        {
            "number": 99999,
            "name": "99999 - ANOTHER STATION",
            "address": "Rue Exemple",
            "commune": "Lyon",
            "status": "CLOSED",
            "availability": "Gris",
            "lat": 45.75,
            "lng": 4.85,
            "bike_stands": 10,
            "available_bikes": 0,
            "available_bike_stands": 0,
            "banking": True,
            "last_update": "2026-04-10 15:00:00+02:00",
            "total_stands": {
                "availabilities": {
                    "bikes": 0,
                    "electricalBikes": 0,
                    "electricalInternalBatteryBikes": 0,
                    "electricalRemovableBatteryBikes": 0,
                    "mechanicalBikes": 0,
                    "stands": 0,
                },
                "capacity": 10,
            },
        },
    ],
}


SAMPLE_PARK_AND_RIDE_RESPONSE = {
    "fields": [],
    "nb_results": 3,
    "values": [
        {
            "capacite": 730,
            "gid": 609,
            "horaires": "Ouvert de 4h30 à 1h du lundi au jeudi",
            "id": "VAI2",
            "last_update": "2026-06-19 08:11:00+02:00",
            "last_update_fme": "2026-06-19 08:14:02+02:00",
            "nb_tot_place_dispo": 609,
            "nom": "Vaise 2",
            "p_surv": True,
            "place_handi": 18,
        },
        {
            "capacite": 655,
            "gid": 606,
            "horaires": "Ouvert de 4h30 à 1h00 du lundi au jeudi",
            "id": "GOR",
            "last_update": None,
            "last_update_fme": "2026-06-19 08:14:02+02:00",
            "nb_tot_place_dispo": 0,
            "nom": "Gorge de Loup",
            "p_surv": False,
            "place_handi": 19,
        },
    ],
}


def _make_client_with_response(response_json: dict) -> DataGrandLyonClient:
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value=response_json)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    return DataGrandLyonClient(session)


def test_client_without_credentials():
    session = MagicMock(spec=aiohttp.ClientSession)
    client = DataGrandLyonClient(session)
    assert client._session is session
    assert client._auth is None


def test_client_with_credentials():
    session = MagicMock(spec=aiohttp.ClientSession)
    client = DataGrandLyonClient(session, username="user", password="pass")
    assert client._session is session
    assert isinstance(client._auth, aiohttp.BasicAuth)


@pytest.mark.asyncio
async def test_get_tcl_passages_returns_all():
    client = _make_client_with_response(SAMPLE_TCL_RESPONSE)
    passages = await client.get_tcl_passages()

    assert len(passages) == 3
    assert passages[0] == TclPassage(
        id=30101,
        ligne="A",
        direction="Vaulx-en-Velin La Soie",
        delai_passage="25 min",
        type=TclPassageType.THEORETICAL,
        heure_passage=datetime(2026, 4, 10, 16, 52, 43),
        id_tarret_destination=36394,
        course_theorique="301_301A-0805V_00701083",
    )
    assert passages[2].ligne == "B"
    assert passages[2].id == 99999


@pytest.mark.asyncio
async def test_get_velov_stations_returns_all():
    client = _make_client_with_response(SAMPLE_VELOV_RESPONSE)
    stations = await client.get_velov_stations()

    assert len(stations) == 2
    assert stations[0] == VelovStation(
        number=15002,
        name="15002 - ST PRIEST - CITE BERLIET",
        address="Place Steven Spielberg",
        commune="Saint-Priest",
        status=VelovStationStatus.OPEN,
        availability=VelovAvailabilityLevel.GREEN,
        lat=45.70597,
        lng=4.900886,
        bike_stands=20,
        available_bikes=7,
        available_bike_stands=13,
        banking=False,
        last_update=datetime.fromisoformat("2026-04-10 16:28:08+02:00"),
        total_stands=VelovBikeStandAvailability(
            bikes=7,
            electrical_bikes=3,
            electrical_internal_battery_bikes=3,
            electrical_removable_battery_bikes=0,
            mechanical_bikes=4,
            stands=13,
            capacity=20,
        ),
    )
    assert stations[1].number == 99999
    assert stations[1].status == VelovStationStatus.CLOSED


@pytest.mark.asyncio
async def test_get_velov_stations_no_auth():
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value=SAMPLE_VELOV_RESPONSE)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    client = DataGrandLyonClient(session, username="user", password="pass")
    await client.get_velov_stations()

    _, kwargs = session.get.call_args
    assert "auth" not in kwargs


@pytest.mark.asyncio
async def test_get_tcl_stops_returns_all():
    client = _make_client_with_response(SAMPLE_TCL_STOPS_RESPONSE)
    stops = await client.get_tcl_stops()

    assert len(stops) == 3
    assert stops[0] == TclStop(
        id=1041,
        gid=31977,
        adresse="111 AVENUE PAUL SANTY",
        ascenseur=False,
        commune="Lyon 8e Arrondissement",
        desserte=["C25"],
        escalator=False,
        insee="69388",
        last_update=datetime.fromisoformat("2026-06-05 01:46:00"),
        lat=45.727741988888,
        lon=4.878116954554,
        nom="Général André",
        pmr=True,
    )


@pytest.mark.asyncio
async def test_get_tcl_stops_null_last_update():
    client = _make_client_with_response(SAMPLE_TCL_STOPS_RESPONSE)
    stops = await client.get_tcl_stops()

    assert stops[1].id == 21844
    assert stops[1].last_update is None
    assert stops[1].adresse is None


@pytest.mark.asyncio
async def test_get_tcl_stops_desserte_parsed():
    client = _make_client_with_response(SAMPLE_TCL_STOPS_RESPONSE)
    stops = await client.get_tcl_stops()

    assert stops[1].desserte == ["JD617", "JD621"]
    assert stops[2].desserte == ["204", "215", "JD473"]


@pytest.mark.asyncio
async def test_get_tcl_park_and_rides_returns_all():
    client = _make_client_with_response(SAMPLE_PARK_AND_RIDE_RESPONSE)
    parks = await client.get_tcl_park_and_rides()

    assert len(parks) == 2
    assert parks[0] == TclParkAndRide(
        id="VAI2",
        gid=609,
        nom="Vaise 2",
        capacite=730,
        place_handi=18,
        horaires="Ouvert de 4h30 à 1h du lundi au jeudi",
        p_surv=True,
        nb_tot_place_dispo=609,
        last_update=datetime.fromisoformat("2026-06-19 08:11:00+02:00"),
        last_update_fme=datetime.fromisoformat("2026-06-19 08:14:02+02:00"),
    )
    assert parks[1].id == "GOR"
    assert parks[1].nb_tot_place_dispo == 0


@pytest.mark.asyncio
async def test_get_tcl_park_and_rides_null_last_update():
    client = _make_client_with_response(SAMPLE_PARK_AND_RIDE_RESPONSE)
    parks = await client.get_tcl_park_and_rides()

    assert parks[1].last_update is None
    assert parks[1].last_update_fme == datetime.fromisoformat(
        "2026-06-19 08:14:02+02:00"
    )
