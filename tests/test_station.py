"""The abandoned 149th St station: the Sopranos' hideout, King Krete with the stolen record."""

from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import SCENES, GameState
from tests.apphelpers import act, choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
STATION = ROOT / "assets" / "scenes" / "station.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def in_the_station(db_file):
    # changed: the crew walks to the station gate, the key opens it, ENTER THE STATION leads in
    save_game(db_file, GameState(current_scene="gate", inventory=["service_key"]))
    at = start_app()
    choose(at, "resume")
    act(at, "enter_station")
    act(at, "enter")
    return at


def test_the_abandoned_station():
    svg = STATION.read_text()
    assert 'id="scene-station"' in svg
    for p in ('id="mosaic-sign"', 'id="abandoned-car"', 'id="tracks"', 'id="platform-edge"',
              'id="flicker-lights"', 'id="fire-barrel"', 'id="dust"'):
        assert p in svg
    assert "149 ST" in part(svg, 'id="mosaic-sign"', "<!-- end mosaic-sign -->")


def test_king_krete_has_the_record_and_the_sopranos_are_with_him():
    svg = STATION.read_text()
    assert "<!-- King Krete" in svg
    assert svg.count("<!-- Sopranos member") == 2
    record = part(svg, 'id="stolen-record"', "<!-- end stolen-record -->")
    assert "THINK" in record and 'data-action="inspect:stolen_record"' in record
    for member in ("Fantastic Needle", "MC Bible", "MC Meyhem", "Portals", "Reekz"):
        assert f"<!-- {member}" in svg


def test_ways_out_and_the_rap_battle_rounds():
    # changed: the rap battle is here now (it was a greyed-out RAP BATTLE button with SOON)
    svg = STATION.read_text()
    assert 'data-action="go_block"' in svg and "BACK TO THE BLOCK" in svg
    # changed: the player chooses who goes first (it used to be ROUND 1: MEYHEM and ROUND 2: BIBLE)
    assert 'data-action="meyhem_first"' in svg and 'data-action="bible_first"' in svg and "WHO GOES FIRST?" in svg
    assert 'data-action="rap_battle"' not in svg


def test_krete_challenges_them_to_a_battle():
    dialogue = SCENES["station"]["dialogue"]
    assert dialogue[0][0] == "krete"
    lines = " ".join(line for _, line in dialogue)
    assert "MIC" in lines and "RHYME BOOK" in lines
    svg = STATION.read_text()
    for i in range(len(dialogue)):
        assert f'data-overlay="talk-{i}"' in svg
    assert "song" in SCENES["station"]["things"]["stolen_record"]


def test_inside_the_station(db_file):
    at = in_the_station(db_file)
    shown = picture(at)
    assert shows_picture(at, "scene-station")
    assert len(at.main.header) == 0 and len(at.main.markdown) == 0 and len(at.main.button) == 0
    assert shown["show"][0] == "talk-0"
    assert {"go_block", "next", "inspect:stolen_record", "meyhem_first", "bible_first"} <= set(shown["enabled"])  # changed: who goes first


def test_looking_at_the_record_and_talking_change_nothing(db_file):
    at = in_the_station(db_file)
    saved = load_game(db_file)
    choose(at, "next", screen="picture")
    choose(at, "inspect:stolen_record", screen="picture")
    assert "inspect-stolen_record" in picture(at)["show"]
    choose(at, "close", screen="picture")
    assert load_game(db_file) == saved


def test_back_to_the_block_from_the_station(db_file):
    at = in_the_station(db_file)
    act(at, "go_block")
    assert shows_picture(at, "scene-block")
    assert load_game(db_file) == GameState(current_scene="block", inventory=["service_key"])


def test_station_asset_matches_its_source():
    assert STATION.read_text() == build.station_scene()
