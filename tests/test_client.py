from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from transports_commun_lyon import Passage, PassageType, TCLClient

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
