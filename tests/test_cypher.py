"""The b-boy cypher in front of the corner store: click it, JOIN IN, and the view goes close up
on the cypher, where Reekz battles (test_cypher_battle.py). Only for show: nothing is saved."""

from pathlib import Path

import pytest

from db import load_game, save_game
from logic import SCENES, SONGS, GameState
from tests.apphelpers import choose, picture, shows_picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
BLOCK = (ROOT / "assets" / "scenes" / "block.svg").read_text()


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def on_the_block(db_file):
    # changed: the cypher only shows up after Needle has been to Grandmaster Flash
    save_game(db_file, GameState(current_scene="block", inventory=[], met_flash=True))
    at = start_app()
    choose(at, "resume")
    return at


def test_the_cypher_can_be_clicked():
    assert SCENES["block"]["things"]["cypher"]["join"] is True
    cypher = part(BLOCK, 'id="cypher"', "<!-- end cypher -->")
    assert 'data-action="inspect:cypher"' in cypher
    sign = part(BLOCK, 'data-overlay="inspect-cypher"', "<!-- end sign -->")
    assert 'data-action="join:cypher"' in sign and "JOIN IN" in sign
    assert 'data-action="close"' in sign and "LEAVE IT" in sign


def test_join_in_goes_close_up_with_apache_playing(db_file):
    # changed: the close-up is the cypher battle now (test_cypher_battle.py); this checks the way in and out
    at = on_the_block(db_file)
    saved = load_game(db_file)
    choose(at, "inspect:cypher", screen="picture")
    assert "join:cypher" in picture(at)["enabled"]
    choose(at, "join:cypher", screen="picture")
    shown = svg_screen(at, "cypher")
    assert shown is not None and 'id="cypher-screen"' in shown["svg"]
    assert "leave_cypher" in shown["enabled"]
    assert shown["audio"]["src"] == f"app/static/{SONGS['apache']['file']}"  # the b-boy anthem
    assert picture(at) is None
    assert load_game(db_file) == saved  # just for show

    choose(at, "leave_cypher", screen="cypher")
    assert svg_screen(at, "cypher") is None
    assert shows_picture(at, "scene-block")
    assert picture(at)["audio"]["src"] is None  # the music stops
    assert load_game(db_file) == saved


# changed: the close-up of Reekz walking in and breaking on a loop became the battle, whose
# pictures are tested in test_cypher_battle.py
