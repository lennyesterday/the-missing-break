"""Needle's secret joint: once the crew has won it back, it can be played in the basement."""

from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import RECORDS, SONGS, GameState
from tests.apphelpers import choose, picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
HQ = ROOT / "assets" / "scenes" / "hq.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def resume_in_hq(db_file, inventory):
    save_game(db_file, GameState(current_scene="hq", inventory=inventory))
    at = start_app()
    choose(at, "resume")
    return at


def test_think_about_it_is_a_record_with_its_song():
    record = RECORDS["think_about_it"]
    assert record["artist"] == "Lyn Collins" and record["year"] == 1972
    assert record["requires"] == "vinyl"  # only once the crew has it back
    assert (ROOT / "static" / SONGS[record["song"]]["file"]).is_file()


def test_before_it_is_won_back_only_the_empty_sleeve(db_file):
    at = resume_in_hq(db_file, ["service_key"])
    shown = picture(at)
    assert "pick:think_about_it" not in shown["enabled"]
    assert "inspect:empty_sleeve" in shown["enabled"]
    assert "lacks-vinyl" in shown["show"]


def test_once_it_is_won_back_it_can_be_played(db_file):
    at = resume_in_hq(db_file, ["rhyme_book", "service_key", "vinyl"])
    shown = picture(at)
    assert "pick:think_about_it" in shown["enabled"]
    assert "inspect:empty_sleeve" not in shown["enabled"]  # the sleeve isn't empty any more
    saved = load_game(db_file)

    choose(at, "pick:think_about_it", screen="picture")
    choose(at, "play_record:think_about_it", screen="picture")

    turntable = svg_screen(at, "turntable")
    assert 'id="record-think_about_it"' in turntable["svg"]
    assert turntable["audio"]["src"] == "app/static/audio/records/think_about_it.mp3"
    assert load_game(db_file) == saved  # still only for show


def test_the_basement_shows_the_empty_or_the_full_sleeve():
    svg = HQ.read_text()
    empty = svg[svg.index('id="empty-sleeve"') - 60:svg.index('id="empty-sleeve"')]
    assert 'data-overlay="lacks-vinyl"' in empty
    assert 'data-action="pick:think_about_it"' in svg
    full = svg[svg.index('data-action="pick:think_about_it"') - 200:svg.index('data-action="pick:think_about_it"')]
    assert "has-vinyl" in full
    assert 'data-overlay="needle-busy pick-think_about_it"' in svg


def test_its_turntable_view():
    svg = (ROOT / "assets" / "records" / "think_about_it.svg").read_text()
    assert "THINK (ABOUT IT)" in svg and "LYN COLLINS" in svg and "1972" in svg
    assert svg == build.turntable_screen("think_about_it")
