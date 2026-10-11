"""The basement's background sound: only on the basement screen, fades out for a record."""

from pathlib import Path

import pytest

from logic import SCENES, SONGS
from tests.apphelpers import act, choose, picture, start_app, start_new_game, svg_screen

ROOT = Path(__file__).parent.parent
SRC = "app/static/audio/ambience/basement.wav"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def test_the_basement_has_its_own_background_sound():
    song = SONGS[SCENES["hq"]["ambience"]]
    assert (ROOT / "static" / song["file"]).is_file()
    assert (ROOT / "art" / "ambience.py").is_file()  # how it was made: python -m art.ambience


def test_it_plays_on_the_basement_screen(db_file):
    at = start_app()
    start_new_game(at)
    assert picture(at)["ambience"] == SRC


def test_it_fades_out_for_a_record_and_comes_back(db_file):
    at = start_app()
    start_new_game(at)
    choose(at, "pick:apache", screen="picture")
    assert picture(at)["ambience"] is None              # fades out as soon as a sleeve is pressed
    choose(at, "play_record:apache", screen="picture")
    assert svg_screen(at, "turntable")["ambience"] is None
    choose(at, "back", screen="turntable")
    assert picture(at)["ambience"] == SRC               # back in the basement: it comes back


def test_it_is_only_in_the_basement(db_file):
    at = start_app()
    # changed: the home screen has its own music now (the intro song), not the basement sound
    assert svg_screen(at, "home")["ambience"] != SRC
    start_new_game(at)
    act(at, "go_block")
    # changed: the block has its own background sound now (test_ambiences.py), not the basement's
    assert picture(at)["ambience"] != SRC


def test_the_page_loops_and_fades_it():
    app = (ROOT / "app.py").read_text()
    assert "ambience" in app and ".loop = true" in app and "fadeTo" in app
