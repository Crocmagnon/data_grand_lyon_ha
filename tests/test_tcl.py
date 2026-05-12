from datetime import datetime

from data_grand_lyon_ha import (
    TclPassage,
    TclPassageType,
    filter_tcl_passages_by_line,
    filter_tcl_passages_by_stop,
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
