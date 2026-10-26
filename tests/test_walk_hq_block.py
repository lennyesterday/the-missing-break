"""The walk between the basement and the block: from the HQ the crew walks down the street
under the el to the basketball court, and back the same way (facing the other way). Each walk
goes on into the next place by itself when it's over (or with SKIP)."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import GameState
from tests.apphelpers import choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
THERE = ROOT / "assets" / "walks" / "hq__block.svg"
BACK = ROOT / "assets" / "walks" / "block__hq.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def at_the(db_file, scene, inventory=()):
    save_game(db_file, GameState(current_scene=scene, inventory=list(inventory)))
    at = start_app()
    choose(at, "resume")
    return at


@pytest.mark.parametrize("scene, action, walk, arrives", [
    ("hq", "go_block", "assets/walks/hq__block.svg", "scene-block"),
    ("block", "go_hq", "assets/walks/block__hq.svg", "scene-hq"),
])
def test_the_crew_walks_between_the_basement_and_the_block(db_file, scene, action, walk, arrives):
    at = at_the(db_file, scene)
    choose(at, action, screen="picture")
    assert at.session_state["walk"] == walk
    assert picture(at)["enabled"] == ["enter"]
    assert load_game(db_file).current_scene != scene  # the move is saved when they set off
    choose(at, "enter", screen="picture")              # it goes on by itself at the end (or SKIP)
    assert shows_picture(at, arrives)


@pytest.mark.parametrize("path", [THERE, BACK])
def test_it_goes_on_by_itself_or_with_skip(path):
    svg = path.read_text()
    end = float(re.search(r'<svg[^>]*data-auto-delay="([\d.]+)"', svg).group(1))
    assert re.search(r'<svg[^>]*data-auto-action="enter"', svg) and end >= 4
    skip = svg[svg.index('aria-label="Skip the walk"') - 120:]
    assert 'data-action="enter"' in skip[:200] and "SKIP" in skip


def test_from_the_hq_door_to_the_court():
    svg = THERE.read_text()
    for part in ('id="hq-door"', 'id="court-gate"', 'id="hoop"'):
        assert part in svg, part
    for member in ("Fantastic Needle", "MC Bible", "Reekz", "Portals (denim"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert f"<!-- {member}" in svg, member
    assert re.search(r'data-overlay="has-rhyme_book[" ]', svg) and re.search(r'data-overlay="lacks-rhyme_book[" ]', svg)


def test_back_the_same_way_facing_the_other_way():
    there, back = THERE.read_text(), BACK.read_text()
    street = lambda svg: svg[svg.index("<!-- the street from the HQ to the court -->"):svg.index("<!-- end street -->")]
    assert street(there) == street(back)                  # the same street
    assert 'id="crew-walking-back" transform="translate(800 0) scale(-1 1)"' in back  # mirrored: walking left
    assert "crew-walking-back" not in there


@pytest.mark.parametrize("asset, make", [("assets/walks/hq__block.svg", build.walk_hq_to_block),
                                         ("assets/walks/block__hq.svg", build.walk_block_to_hq)])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()
