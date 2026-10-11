"""Don't Sweat the Technique plays on the home screen and through the story intro."""

from pathlib import Path

import pytest

from db import save_game
from logic import INTRO_MUSIC, SONGS, GameState
from tests.apphelpers import svg_screen, choose, home_screen, intro_screen, picture, start_app

ROOT = Path(__file__).parent.parent
SRC = "app/static/audio/music/dont_sweat_the_technique.mp3"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def test_the_intro_song_ships_with_the_game():
    song = SONGS[INTRO_MUSIC]
    assert song["title"] == "Don't Sweat the Technique"
    assert (ROOT / "static" / song["file"]).is_file()
    assert "Eric B. & Rakim" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()


def test_it_plays_on_the_home_screen(db_file):
    at = start_app()
    assert home_screen(at)["ambience"] == SRC


def test_it_keeps_playing_through_the_story_intro(db_file):
    at = start_app()
    choose(at, "start")
    assert intro_screen(at)["ambience"] == SRC
    choose(at, "go", screen="intro")
    assert svg_screen(at, "escape")["ambience"] is None  # changed: LET'S GO fades the song out, before the escape
    choose(at, "arrive", screen="escape")
    assert picture(at)["ambience"] != SRC  # in the game: the basement's own sound takes over


def test_resume_goes_straight_to_the_scene_sound(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=[]))
    at = start_app()
    assert home_screen(at)["ambience"] == SRC
    choose(at, "resume")
    # changed: the block has its own background sound now (test_ambiences.py)
    assert picture(at)["ambience"] == f"app/static/{SONGS['block_ambience']['file']}"


def test_the_page_starts_it_on_the_first_click_if_the_browser_blocks_it():
    app = (ROOT / "app.py").read_text()
    assert "pointerdown" in app and "keydown" in app
