"""The way to the old 149th St station. From the block the crew always walks there, following
the Sopranos' tags, to the station gate. Without Rico's key the gate stays chained (A1): back to
the block, and on to Rico's. With it the key opens the gate (A2) and they go in.

changed: the walk used to need the key before it started (enter_station on the block); now the
gate is its own place, where the key is needed."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import LOCKED_STATION_MESSAGE, SCENES, GameState
from tests.apphelpers import act, choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
GATE = ROOT / "assets" / "scenes" / "gate.svg"
UNLOCK = ROOT / "assets" / "walks" / "gate__station.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def at_the(db_file, scene, inventory=()):
    save_game(db_file, GameState(current_scene=scene, inventory=list(inventory)))
    at = start_app()
    choose(at, "resume")
    return at


# --- the rules ---

def test_the_gate():
    gate = SCENES["gate"]
    assert {a["id"] for a in gate["actions"]} == {"enter_station", "go_block"}
    enter = next(a for a in gate["actions"] if a["id"] == "enter_station")
    assert enter["requires"] == "service_key" and enter["target"] == "station"
    assert enter["locked_message"] == LOCKED_STATION_MESSAGE


# --- in the app ---

def test_the_crew_walks_to_the_gate_even_without_the_key(db_file):
    at = at_the(db_file, "block")
    act(at, "go_gate")
    assert shows_picture(at, "scene-gate")
    assert {"enter_station", "go_block"} <= set(picture(at)["enabled"])
    assert load_game(db_file).current_scene == "gate"


def test_without_the_key_the_gate_stays_shut(db_file):
    # A1, in the picture: the message comes up, nothing moves, nothing is saved
    at = at_the(db_file, "gate")
    saved = load_game(db_file)
    act(at, "enter_station")
    assert "rejected-enter_station" in picture(at)["show"]
    sign = part(picture(at)["svg"], 'data-overlay="rejected-enter_station"', "<!-- end rejected -->")
    assert LOCKED_STATION_MESSAGE.upper() in sign and "RICO" in sign
    assert at.session_state["game"].current_scene == "gate"
    assert at.session_state["walk"] is None
    assert load_game(db_file) == saved


def test_back_to_the_block_and_on_to_ricos(db_file):
    at = at_the(db_file, "gate")
    act(at, "go_block")
    assert shows_picture(at, "scene-block")
    act(at, "go_record_shop")
    assert at.session_state["game"].current_scene == "record_shop"


def test_with_the_key_the_gate_opens_and_they_go_in(db_file):
    # A2, in the picture
    at = at_the(db_file, "gate", ["service_key"])
    assert "has-service_key" in picture(at)["show"]
    act(at, "enter_station")
    assert at.session_state["walk"] == "assets/walks/gate__station.svg"
    assert shows_picture(at, "walk-gate-station")
    assert picture(at)["enabled"] == ["enter"]
    saved = load_game(db_file)  # changed: the save also remembers the places left (specs/story-line-fixes.md)
    assert (saved.current_scene, saved.inventory) == ("station", ["service_key"])
    act(at, "enter")
    assert shows_picture(at, "scene-station")


def test_from_the_station_back_to_the_block(db_file):
    at = at_the(db_file, "station", ["service_key"])
    act(at, "go_block")
    assert at.session_state["game"].current_scene == "block"


def test_bible_with_or_without_his_book(db_file):
    for path in (GATE, UNLOCK):
        svg = path.read_text()
        assert re.search(r'data-overlay="has-rhyme_book[" ]', svg), path
        assert re.search(r'data-overlay="lacks-rhyme_book[" ]', svg), path


# --- the pictures ---

def test_the_crew_walks_in_following_the_sopranos_tags():
    # changed: they walk in on the walk from the block (block__gate, with SKIP), not at the gate itself
    svg = (ROOT / "assets" / "walks" / "block__gate.svg").read_text()
    for member in ("Fantastic Needle", "MC Bible", "Reekz", "Portals (denim"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert f"<!-- {member}" in svg, member
    assert 'attributeName="transform" type="translate" from="0 0"' in svg  # they walk in
    trail = part(svg, 'id="sopranos-trail"', "<!-- end sopranos-trail -->")
    assert len(re.findall(r'class="tag"[^>]*>(Sopranos|Krete|SF|Krete 77)', trail)) >= 5


def test_the_chained_gate_and_the_buttons():
    svg = GATE.read_text()
    entrance = part(svg, 'id="station-entrance"', "<!-- end station-entrance -->")
    assert "149 ST" in entrance and 'id="chain"' in entrance and 'id="padlock"' in entrance
    assert "data-action" not in entrance
    assert 'data-action="enter_station"' in svg and "OPEN THE GATE" in svg
    assert 'data-action="go_block"' in svg and "BACK TO THE BLOCK" in svg
    assert 'data-overlay="has-service_key"' in svg


def test_the_key_opens_the_gate():
    svg = UNLOCK.read_text()
    assert 'id="unlock"' in svg
    assert re.search(r'id="padlock"[\s\S]*?<animate', part(svg, 'id="station-entrance"', "<!-- end station-entrance -->"))
    enter = part(svg, 'data-action="enter"', "<!-- end enter -->")
    assert "ENTER THE STATION" in enter and 'to="visible"' in enter


@pytest.mark.parametrize("asset, make", [("assets/scenes/gate.svg", build.gate_scene),
                                         ("assets/walks/gate__station.svg", build.walk_gate_to_station)])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()


def test_no_walk_file_for_the_old_route():
    assert not (ROOT / "assets" / "walks" / "block__station.svg").exists()
