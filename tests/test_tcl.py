from datetime import datetime

from data_grand_lyon_ha import (
    TclParkAndRide,
    TclPassage,
    TclPassageType,
    TclStop,
    filter_tcl_passages_by_line,
    filter_tcl_passages_by_lines_stops,
    filter_tcl_passages_by_stop,
    find_tcl_park_and_ride_by_id,
    find_tcl_stop_by_id,
    sort_tcl_passages_by_time,
)

PASSAGES = [
    TclPassage(
        id=30101,
        ligne="A",
        direction="Vaulx-en-Velin La Soie",
        delai_passage="25 min",
        type=TclPassageType.THEORETICAL,
        heure_passage=datetime(2026, 4, 10, 16, 52, 43),
        id_tarret_destination=36394,
        course_theorique="course_1",
    ),
    TclPassage(
        id=30101,
        ligne="A",
        direction="Vaulx-en-Velin La Soie",
        delai_passage="3 min",
        type=TclPassageType.ESTIMATED,
        heure_passage=datetime(2026, 4, 10, 16, 30, 0),
        id_tarret_destination=36394,
        course_theorique="course_2",
    ),
    TclPassage(
        id=30101,
        ligne="A",
        direction="Vaulx-en-Velin La Soie",
        delai_passage="40 min",
        type=TclPassageType.THEORETICAL,
        heure_passage=datetime(2026, 4, 10, 17, 10, 0),
        id_tarret_destination=36394,
        course_theorique="course_3",
    ),
    TclPassage(
        id=99999,
        ligne="B",
        direction="Charpennes",
        delai_passage="10 min",
        type=TclPassageType.THEORETICAL,
        heure_passage=datetime(2026, 4, 10, 16, 37, 0),
        id_tarret_destination=42575,
        course_theorique="course_4",
    ),
]


def test_filter_by_line():
    result = filter_tcl_passages_by_line(PASSAGES, "A")
    assert len(result) == 3
    assert all(p.ligne == "A" for p in result)


def test_filter_by_line_no_match():
    result = filter_tcl_passages_by_line(PASSAGES, "C")
    assert result == []


def test_filter_by_stop():
    result = filter_tcl_passages_by_stop(PASSAGES, 30101)
    assert len(result) == 3
    assert all(p.id == 30101 for p in result)


def test_filter_by_stop_no_match():
    result = filter_tcl_passages_by_stop(PASSAGES, 12345)
    assert result == []


def test_sort_by_time():
    result = sort_tcl_passages_by_time(PASSAGES)
    times = [p.heure_passage for p in result]
    assert times == sorted(times)


def test_sort_already_sorted():
    already = sorted(PASSAGES, key=lambda p: p.heure_passage)
    result = sort_tcl_passages_by_time(already)
    assert result == already


def test_filter_by_lines_stops():
    result = filter_tcl_passages_by_lines_stops(PASSAGES, [("A", 30101), ("B", 99999)])
    assert len(result) == 2
    assert len(result[("A", 30101)]) == 3
    assert all(p.ligne == "A" and p.id == 30101 for p in result[("A", 30101)])
    assert len(result[("B", 99999)]) == 1
    assert result[("B", 99999)][0].ligne == "B"


def test_filter_by_lines_stops_no_match():
    result = filter_tcl_passages_by_lines_stops(PASSAGES, [("C", 12345)])
    assert result == {("C", 12345): []}


def test_filter_by_lines_stops_partial_match():
    result = filter_tcl_passages_by_lines_stops(PASSAGES, [("A", 30101), ("C", 12345)])
    assert len(result[("A", 30101)]) == 3
    assert result[("C", 12345)] == []


STOPS = [
    TclStop(
        id=1041,
        gid=31977,
        adresse="111 AVENUE PAUL SANTY",
        ascenseur=False,
        commune="Lyon 8e Arrondissement",
        desserte=["C25"],
        escalator=False,
        insee="69388",
        last_update=datetime(2026, 6, 5, 1, 46, 0),
        lat=45.727741988888,
        lon=4.878116954554,
        nom="Général André",
        pmr=True,
    ),
    TclStop(
        id=21844,
        gid=37682,
        adresse=None,
        ascenseur=None,
        commune=None,
        desserte=["JD617", "JD621"],
        escalator=None,
        insee=None,
        last_update=None,
        lat=45.801439,
        lon=4.396345,
        nom="Villecheneve Montlit",
        pmr=False,
    ),
]


def test_find_stop_by_id_found():
    result = find_tcl_stop_by_id(STOPS, 1041)
    assert result is not None
    assert result.id == 1041
    assert result.nom == "Général André"


def test_find_stop_by_id_not_found():
    assert find_tcl_stop_by_id(STOPS, 99999) is None


def test_find_stop_by_id_empty_list():
    assert find_tcl_stop_by_id([], 1041) is None


PARKS = [
    TclParkAndRide(
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
    ),
    TclParkAndRide(
        id="GOR",
        gid=606,
        nom="Gorge de Loup",
        capacite=655,
        place_handi=19,
        horaires="Ouvert de 4h30 à 1h00 du lundi au jeudi",
        p_surv=False,
        nb_tot_place_dispo=0,
        last_update=None,
        last_update_fme=datetime.fromisoformat("2026-06-19 08:14:02+02:00"),
    ),
]


def test_find_park_and_ride_by_id_found():
    result = find_tcl_park_and_ride_by_id(PARKS, "VAI2")
    assert result is not None
    assert result.id == "VAI2"
    assert result.nom == "Vaise 2"


def test_find_park_and_ride_by_id_not_found():
    assert find_tcl_park_and_ride_by_id(PARKS, "XXXX") is None


def test_find_park_and_ride_by_id_empty_list():
    assert find_tcl_park_and_ride_by_id([], "VAI2") is None


def test_composing_filters():
    """Filters compose: filter by line, then stop, then deduplicate, then sort."""
    result = filter_tcl_passages_by_line(PASSAGES, "A")
    result = filter_tcl_passages_by_stop(result, 30101)
    result = sort_tcl_passages_by_time(result)

    assert len(result) == 3
    assert result[0].course_theorique == "course_2"
    assert result[0].type == TclPassageType.ESTIMATED
    assert result[1].course_theorique == "course_1"
    assert result[2].course_theorique == "course_3"
    assert result[0].heure_passage < result[1].heure_passage
