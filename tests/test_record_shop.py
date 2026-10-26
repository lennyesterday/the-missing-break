"""Rico's record shop: the walk ends at the door, ENTER RICO'S leads inside."""

from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import SCENES, GameState
from tests.apphelpers import act, choose, offered, picture, shows_picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
SHOP = ROOT / "assets" / "scenes" / "record_shop.svg"
WALK = ROOT / "assets" / "walks" / "block__record_shop.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def in_the_shop(at):
    start_new_game(at)
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(at, "go_record_shop")
    act(at, "enter")


def test_the_walk_ends_with_an_enter_button_once_the_crew_is_at_the_door():
    svg = WALK.read_text()
    enter = svg[svg.index('data-action="enter"'):]
    enter = enter[:enter.index("<!-- end enter -->")]
    assert "ENTER RICO'S" in enter
    assert 'visibility="hidden"' in enter and '<set attributeName="visibility" to="visible" begin="4s"' in enter


def test_inside_ricos_record_shop():
    svg = SHOP.read_text()
    assert 'id="scene-record-shop"' in svg
    for part in ('id="record-wall"', 'id="record-bins"', 'id="counter"', 'id="drawer"', 'id="neon-sign"',
                 'id="listening-deck"'):
        assert part in svg
    for genre in ("SOUL", "FUNK", "BREAKS", "LATIN", "DISCO"):
        assert f">{genre}</text>" in svg
    assert "<!-- Rico" in svg
    for member in ("Fantastic Needle", "MC Bible", "MC Meyhem", "Portals", "Reekz"):
        assert f"<!-- {member}" in svg
    assert 'data-action="go_block"' in svg and "BACK TO THE BLOCK" in svg


def test_the_key_is_in_the_drawer_until_it_is_taken():
    svg = SHOP.read_text()
    key = svg[svg.index('data-overlay="offer-take_service_key"'):]
    assert 'data-action="take_service_key"' in key[:key.index("<!-- end key -->")]
    assert 'data-overlay="done-take_service_key"' in svg  # the "you got" message
    assert "OLD MTA SERVICE KEY" in svg


def test_rico_tells_them_about_the_station_and_the_key():
    dialogue = SCENES["record_shop"]["dialogue"]
    assert dialogue[0][0] == "rico"
    lines = " ".join(line for _, line in dialogue)
    assert "149TH ST STATION" in lines and "MTA" in lines and "KEY" in lines and "DRAWER" in lines
    svg = SHOP.read_text()
    for i in range(len(dialogue)):
        assert f'data-overlay="talk-{i}"' in svg


def test_shop_is_played_inside_the_picture(db_file):
    at = start_app()
    in_the_shop(at)
    shown = picture(at)
    assert shows_picture(at, "scene-record-shop")
    assert len(at.main.header) == 0 and len(at.main.markdown) == 0 and len(at.main.button) == 0
    assert shown["show"][0] == "talk-0"
    assert "offer-take_service_key" in shown["show"]
    assert {"take_service_key", "go_block", "next"} <= set(shown["enabled"])


def test_taking_the_key_in_the_shop(db_file):
    at = start_app()
    in_the_shop(at)

    act(at, "take_service_key")

    assert at.session_state["game"].inventory == ["service_key"]
    saved = load_game(db_file)  # changed: the save also remembers the places left (specs/story-line-fixes.md)
    assert (saved.current_scene, saved.inventory) == ("record_shop", ["service_key"])
    shown = picture(at)
    assert "offer-take_service_key" not in shown["show"]  # the drawer is empty now (PT R3)
    assert "done-take_service_key" in shown["show"]       # "you got the key"
    assert "take_service_key" not in shown["enabled"]
    choose(at, "next", screen="picture")                  # any click puts the message away
    assert "done-take_service_key" not in picture(at)["show"]


def test_back_to_the_block_from_the_shop(db_file):
    at = start_app()
    in_the_shop(at)
    act(at, "go_block")
    assert at.session_state["game"].current_scene == "block"


def test_resume_in_the_shop_shows_the_inside(db_file):
    save_game(db_file, GameState(current_scene="record_shop", inventory=["service_key"]))
    at = start_app()
    choose(at, "resume")
    assert shows_picture(at, "scene-record-shop")
    assert "offer-take_service_key" not in picture(at)["show"]
    assert "take_service_key" not in offered(at)


def test_shop_asset_matches_its_source():
    assert SHOP.read_text() == build.record_shop_scene()
