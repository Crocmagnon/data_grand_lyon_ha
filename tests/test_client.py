from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from data_grand_lyon_ha import (
    DataGrandLyonClient,
    TclAlert,
    TclAlertSeverityType,
    TclAlertType,
    TclLinePictogram,
    TclParkAndRide,
    TclPassage,
    TclPassageType,
    TclStop,
    VelovAvailabilityLevel,
    VelovBikeStandAvailability,
    VelovStation,
    VelovStationStatus,
)

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


SAMPLE_TCL_ALERTS_RESPONSE = {
    "fields": [],
    "nb_results": 2,
    "values": [
        {
            "cause": "événement",
            "debut": "2026-06-21 04:30:00",
            "fin": "2026-06-22 01:30:00",
            "last_update_fme": "2026-06-19 09:15:05",
            "ligne_cli": "A",
            "ligne_com": "A",
            "listeobjet": "A",
            "message": "Dans le cadre de la fête de la Musique...",
            "mode": "Métro",
            "n": 1,
            "niveauseverite": 30,
            "titre": "Fête de la Musique du 21/06",
            "type": "Information",
            "typeobjet": "line",
            "typeseverite": "OTHER_EFFECT",
        },
        {
            "cause": "travaux",
            "debut": "2026-05-28 04:30:00",
            "fin": "2026-07-26 02:30:00",
            "last_update_fme": "2026-06-19 09:15:05",
            "ligne_cli": "27",
            "ligne_com": "27",
            "listeobjet": "27",
            "message": "Travaux sur la ligne 27.",
            "mode": "Bus",
            "n": 2,
            "niveauseverite": 20,
            "titre": "Travaux ligne 27",
            "type": "Perturbation",
            "typeobjet": "line",
            "typeseverite": "SIGNIFICANT_DELAYS",
        },
    ],
}


SAMPLE_PICTOGRAMS_CSV = (
    "code_ligne;picto_mode;picto_ligne;picto_complet\n"
    "10;mode_bus.svg;10_ligne.svg;10.svg\n"
    "104A;mode_bus.svg;104A_ligne.svg;104A.svg\n"
    "A;mode_metro.svg;A_ligne.svg;A.svg\n"
)


def _make_client_with_response(response_json: dict) -> DataGrandLyonClient:
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value=response_json)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    return DataGrandLyonClient(session)


def _make_client_with_text(text: str) -> tuple[DataGrandLyonClient, MagicMock]:
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = AsyncMock(return_value=text)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    return DataGrandLyonClient(session), session


def _make_client_with_bytes(data: bytes) -> tuple[DataGrandLyonClient, MagicMock]:
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=data)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    return DataGrandLyonClient(session), session


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
async def test_get_tcl_alerts_returns_all():
    client = _make_client_with_response(SAMPLE_TCL_ALERTS_RESPONSE)
    alerts = await client.get_tcl_alerts()

    assert len(alerts) == 2
    assert alerts[0] == TclAlert(
        type=TclAlertType.INFORMATION,
        cause="événement",
        debut=datetime(2026, 6, 21, 4, 30, 0),
        fin=datetime(2026, 6, 22, 1, 30, 0),
        mode="Métro",
        ligne_com="A",
        ligne_cli="A",
        titre="Fête de la Musique du 21/06",
        message="Dans le cadre de la fête de la Musique...",
        last_update_fme=datetime(2026, 6, 19, 9, 15, 5),
        n=1,
        type_severite=TclAlertSeverityType.OTHER_EFFECT,
        niveau_severite=30,
        type_objet="line",
        liste_objet="A",
    )
    assert alerts[1].ligne_cli == "27"
    assert alerts[1].type == TclAlertType.DISRUPTION
    assert alerts[1].type_severite == TclAlertSeverityType.SIGNIFICANT_DELAYS


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


@pytest.mark.asyncio
async def test_get_tcl_line_pictograms_returns_all():
    client, session = _make_client_with_text(SAMPLE_PICTOGRAMS_CSV)
    lines = await client.get_tcl_line_pictograms()

    assert len(lines) == 3
    assert lines[0] == TclLinePictogram(
        code_ligne="10",
        picto_mode="mode_bus.svg",
        picto_ligne="10_ligne.svg",
        picto_complet="10.svg",
    )
    assert lines[2].code_ligne == "A"
    assert lines[2].picto_complet == "A.svg"

    (url,), _ = session.get.call_args
    assert url.endswith("Liste_pictogrammes_lignes.csv")


@pytest.mark.asyncio
async def test_get_tcl_line_pictograms_zip_returns_bytes():
    client, session = _make_client_with_bytes(b"PK\x03\x04 fake zip")
    data = await client.get_tcl_line_pictograms_zip()

    assert data == b"PK\x03\x04 fake zip"

    (url,), _ = session.get.call_args
    assert url.endswith("Pictogrammes_lignes_complets.zip")
