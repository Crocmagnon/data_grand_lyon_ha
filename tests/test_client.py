from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from data_grand_lyon_ha import (
    Availability,
    Passage,
    PassageType,
    StationStatus,
    TCLClient,
    VelovAvailability,
    VelovStationStatus,
)

SAMPLE_API_RESPONSE = {
    "fields": ["id", "ligne", "direction", "delaipassage", "type", "heurepassage",
               "idtarretdestination", "coursetheorique", "gid", "last_update_fme"],
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


def _make_client_with_response(response_json: dict) -> TCLClient:
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value=response_json)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    return TCLClient(session)


def test_client_without_credentials():
    session = MagicMock(spec=aiohttp.ClientSession)
    client = TCLClient(session)
    assert client._session is session
    assert client._auth is None


def test_client_with_credentials():
    session = MagicMock(spec=aiohttp.ClientSession)
    client = TCLClient(session, username="user", password="pass")
    assert client._session is session
    assert isinstance(client._auth, aiohttp.BasicAuth)


@pytest.mark.asyncio
async def test_get_passages_filters_by_ligne_stop_id_and_type():
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_passages("A", 30101, PassageType.THEORETICAL)

    assert len(passages) == 1
    assert passages[0] == Passage(
        id=30101,
        ligne="A",
        direction="Vaulx-en-Velin La Soie",
        delai_passage="25 min",
        type=PassageType.THEORETICAL,
        heure_passage=datetime(2026, 4, 10, 16, 52, 43),
        id_tarret_destination=36394,
        course_theorique="301_301A-0805V_00701083",
    )


@pytest.mark.asyncio
async def test_get_passages_returns_empty_when_no_match():
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_passages("C", 12345, PassageType.ESTIMATED)
    assert passages == []


@pytest.mark.asyncio
async def test_get_passages_without_type_merges_by_course_theorique():
    """When both T and E exist for the same course_theorique, only E is kept."""
    response = {
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
                "coursetheorique": "course_1",
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
                "coursetheorique": "course_1",
                "gid": 2,
                "last_update_fme": "2026-04-10 16:27:01",
            },
            {
                "id": 30101,
                "ligne": "A",
                "direction": "Vaulx-en-Velin La Soie",
                "delaipassage": "40 min",
                "type": "T",
                "heurepassage": "2026-04-10 17:10:00",
                "idtarretdestination": 36394,
                "coursetheorique": "course_2",
                "gid": 3,
                "last_update_fme": "2026-04-10 16:27:01",
            },
        ],
    }
    client = _make_client_with_response(response)
    passages = await client.get_passages("A", 30101)

    assert len(passages) == 2
    # course_1: E kept, T discarded
    assert passages[0].course_theorique == "course_1"
    assert passages[0].type == PassageType.ESTIMATED
    assert passages[0].heure_passage == datetime(2026, 4, 10, 16, 30, 0)
    # course_2: only T, kept as-is
    assert passages[1].course_theorique == "course_2"
    assert passages[1].type == PassageType.THEORETICAL


@pytest.mark.asyncio
async def test_get_passages_without_type_no_merge_when_different_courses():
    """Passages with different course_theorique are not merged."""
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_passages("A", 30101)

    # SAMPLE_API_RESPONSE has two passages for stop 30101/ligne A with different course_theorique
    assert len(passages) == 2


@pytest.mark.asyncio
async def test_get_passages_with_type_does_not_merge():
    """When passage_type is specified, no merging occurs."""
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_passages("A", 30101, PassageType.THEORETICAL)
    assert len(passages) == 1
    assert passages[0].type == PassageType.THEORETICAL


@pytest.mark.asyncio
async def test_get_passages_estimated_type():
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_passages("A", 30101, PassageType.ESTIMATED)

    assert len(passages) == 1
    assert passages[0].type == PassageType.ESTIMATED
    assert passages[0].heure_passage == datetime(2026, 4, 10, 16, 30, 0)


@pytest.mark.asyncio
async def test_get_passages_sorted_by_heure_passage():
    response = {
        "fields": [],
        "nb_results": 3,
        "values": [
            {
                "id": 100,
                "ligne": "A",
                "direction": "Dir",
                "delaipassage": "30 min",
                "type": "T",
                "heurepassage": "2026-04-10 17:00:00",
                "idtarretdestination": 1,
                "coursetheorique": "c3",
                "gid": 3,
                "last_update_fme": "2026-04-10 16:00:00",
            },
            {
                "id": 100,
                "ligne": "A",
                "direction": "Dir",
                "delaipassage": "5 min",
                "type": "T",
                "heurepassage": "2026-04-10 16:05:00",
                "idtarretdestination": 1,
                "coursetheorique": "c1",
                "gid": 1,
                "last_update_fme": "2026-04-10 16:00:00",
            },
            {
                "id": 100,
                "ligne": "A",
                "direction": "Dir",
                "delaipassage": "15 min",
                "type": "T",
                "heurepassage": "2026-04-10 16:35:00",
                "idtarretdestination": 1,
                "coursetheorique": "c2",
                "gid": 2,
                "last_update_fme": "2026-04-10 16:00:00",
            },
        ],
    }
    client = _make_client_with_response(response)
    passages = await client.get_passages("A", 100, PassageType.THEORETICAL)

    assert len(passages) == 3
    assert passages[0].heure_passage == datetime(2026, 4, 10, 16, 5, 0)
    assert passages[1].heure_passage == datetime(2026, 4, 10, 16, 35, 0)
    assert passages[2].heure_passage == datetime(2026, 4, 10, 17, 0, 0)


@pytest.mark.asyncio
async def test_get_stop_passages_returns_all_passages_for_stop():
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_stop_passages(30101)

    # Two passages with different course_theorique, no merge
    assert len(passages) == 2
    assert passages[0].heure_passage == datetime(2026, 4, 10, 16, 30, 0)
    assert passages[1].heure_passage == datetime(2026, 4, 10, 16, 52, 43)


@pytest.mark.asyncio
async def test_get_stop_passages_merges_by_course_theorique():
    response = {
        "fields": [],
        "nb_results": 2,
        "values": [
            {
                "id": 200,
                "ligne": "B",
                "direction": "Dir",
                "delaipassage": "20 min",
                "type": "T",
                "heurepassage": "2026-04-10 16:50:00",
                "idtarretdestination": 1,
                "coursetheorique": "same_course",
                "gid": 1,
                "last_update_fme": "2026-04-10 16:00:00",
            },
            {
                "id": 200,
                "ligne": "B",
                "direction": "Dir",
                "delaipassage": "18 min",
                "type": "E",
                "heurepassage": "2026-04-10 16:48:00",
                "idtarretdestination": 1,
                "coursetheorique": "same_course",
                "gid": 2,
                "last_update_fme": "2026-04-10 16:00:00",
            },
        ],
    }
    client = _make_client_with_response(response)
    passages = await client.get_stop_passages(200)

    assert len(passages) == 1
    assert passages[0].type == PassageType.ESTIMATED
    assert passages[0].delai_passage == "18 min"


@pytest.mark.asyncio
async def test_get_stop_passages_returns_empty_when_no_match():
    client = _make_client_with_response(SAMPLE_API_RESPONSE)
    passages = await client.get_stop_passages(12345)
    assert passages == []


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


@pytest.mark.asyncio
async def test_get_velov_station_found():
    client = _make_client_with_response(SAMPLE_VELOV_RESPONSE)
    station = await client.get_velov_station(15002)

    assert station == VelovStationStatus(
        number=15002,
        name="15002 - ST PRIEST - CITE BERLIET",
        address="Place Steven Spielberg",
        commune="Saint-Priest",
        status=StationStatus.OPEN,
        availability=Availability.GREEN,
        lat=45.70597,
        lng=4.900886,
        bike_stands=20,
        available_bikes=7,
        available_bike_stands=13,
        banking=False,
        last_update=datetime.fromisoformat("2026-04-10 16:28:08+02:00"),
        total_stands=VelovAvailability(
            bikes=7,
            electrical_bikes=3,
            electrical_internal_battery_bikes=3,
            electrical_removable_battery_bikes=0,
            mechanical_bikes=4,
            stands=13,
            capacity=20,
        ),
    )


@pytest.mark.asyncio
async def test_get_velov_station_not_found():
    client = _make_client_with_response(SAMPLE_VELOV_RESPONSE)
    station = await client.get_velov_station(11111)
    assert station is None


@pytest.mark.asyncio
async def test_get_velov_station_no_auth():
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(return_value=SAMPLE_VELOV_RESPONSE)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=mock_response)

    client = TCLClient(session, username="user", password="pass")
    await client.get_velov_station(15002)

    _, kwargs = session.get.call_args
    assert "auth" not in kwargs
