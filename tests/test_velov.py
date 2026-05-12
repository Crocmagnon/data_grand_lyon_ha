from datetime import datetime

from data_grand_lyon_ha import (
    VelovAvailabilityLevel,
    VelovBikeStandAvailability,
    VelovStation,
    VelovStationStatus,
    find_velov_station_by_id,
)

STATIONS = [
    VelovStation(
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
    ),
    VelovStation(
        number=99999,
        name="99999 - ANOTHER STATION",
        address="Rue Exemple",
        commune="Lyon",
        status=VelovStationStatus.CLOSED,
        availability=VelovAvailabilityLevel.GREY,
        lat=45.75,
        lng=4.85,
        bike_stands=10,
        available_bikes=0,
        available_bike_stands=0,
        banking=True,
        last_update=datetime.fromisoformat("2026-04-10 15:00:00+02:00"),
        total_stands=VelovBikeStandAvailability(
            bikes=0,
            electrical_bikes=0,
            electrical_internal_battery_bikes=0,
            electrical_removable_battery_bikes=0,
            mechanical_bikes=0,
            stands=0,
            capacity=10,
        ),
    ),
]


def test_find_station_found():
    station = find_velov_station_by_id(STATIONS, 15002)
    assert station is not None
    assert station.number == 15002
    assert station.name == "15002 - ST PRIEST - CITE BERLIET"


def test_find_station_not_found():
    station = find_velov_station_by_id(STATIONS, 11111)
    assert station is None


def test_find_station_returns_correct_one():
    station = find_velov_station_by_id(STATIONS, 99999)
    assert station is not None
    assert station.status == VelovStationStatus.CLOSED
