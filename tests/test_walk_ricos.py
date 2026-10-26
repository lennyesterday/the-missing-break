"""The walk between the block and Rico's: from the basketball court down the street under the
el, past the pizzeria and the barbershop, to Rico's Record Shop (ENTER RICO'S at the door), and
back the same way (facing the other way), on to the block by itself. SKIP on both."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import GameState
from tests.apphelpers import choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
THERE = ROOT / "assets" / "walks" / "block__record_shop.svg"
BACK = ROOT / "assets" / "walks" / "record_shop__block.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def street(svg):
    return svg[svg.index("<!-- the street from the court to Rico's -->"):svg.index("<!-- end street -->")]


def test_from_the_court_to_ricos():
    # changed: the walk used to start at the HQ; now it starts at the basketball court
    svg = THERE.read_text()
    s = street(svg)
    assert 'id="court-side"' in s and 'id="hoop"' in s and 'id="ricos-shop"' in s
    assert 'id="hq-door"' not in svg
    for member in ("Fantastic Needle", "MC Bible", "Reekz", "Portals (denim"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert f"<!-- {member}" in svg, member


def test_going_there_ends_at_the_door_or_skips_inside():
    svg = THERE.read_text()
    assert "data-auto-action" not in svg[:300]          # it waits at the door for ENTER RICO'S
    skip = svg[svg.index('aria-label="Skip the walk"') - 120:]
    assert 'data-action="enter"' in skip[:200] and "SKIP" in skip  # SKIP: straight inside


def test_back_the_same_way_on_to_the_block_by_itself():
    there, back = THERE.read_text(), BACK.read_text()
    assert street(there) == street(back)
    assert 'id="crew-walking-back" transform="translate(800 0) scale(-1 1)"' in back
    assert re.search(r'<svg[^>]*data-auto-action="enter"', back)
    skip = back[back.index('aria-label="Skip the walk"') - 120:]
    assert 'data-action="enter"' in skip[:200]


def test_coming_back_from_ricos_in_the_app(db_file):
    save_game(db_file, GameState(current_scene="record_shop", inventory=["service_key"]))
    at = start_app()
    choose(at, "resume")
    choose(at, "go_block", screen="picture")
    assert at.session_state["walk"] == "assets/walks/record_shop__block.svg"
    assert load_game(db_file).current_scene == "block"
    choose(at, "enter", screen="picture")             # by itself at the end, or SKIP
    assert shows_picture(at, "scene-block")


@pytest.mark.parametrize("asset, make", [("assets/walks/block__record_shop.svg", build.walk_block_to_record_shop),
                                         ("assets/walks/record_shop__block.svg", build.walk_record_shop_to_block)])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()
