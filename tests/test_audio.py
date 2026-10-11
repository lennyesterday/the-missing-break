"""Songs in the game: MC Bible's verse plays in round 2 and from the rhyme book's sign."""

from pathlib import Path

import pytest

from db import save_game
from logic import SCENES, SONGS, GameState
from tests.apphelpers import act, choose, picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
APP = (ROOT / "app.py").read_text()


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def resume_at(db_file, scene, inventory):
    save_game(db_file, GameState(current_scene=scene, inventory=inventory))
    at = start_app()
    choose(at, "resume")
    return at


def test_mc_bibles_verse_ships_with_the_game_and_its_credits():
    song = SONGS["mc_bible_verse"]
    assert (ROOT / "static" / song["file"]).is_file()
    assert song["title"] == "MC Bible – Rap Verse"
    assert "Suno" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()


def test_the_verse_belongs_to_round_2_only():
    # changed: the rhyme book can be read now, not listened to; the verse plays only in round 2
    assert "song" not in SCENES["hq"]["things"]["rhyme_book"]
    # changed: the station's actions say who raps ("raps"), and the rappers' verses are in logic.RAPPERS
    from logic import RAPPERS
    round_2 = next(a for a in SCENES["station"]["actions"] if a["id"] == "bible_finishes")
    assert round_2["raps"] == ["bible"] and RAPPERS["bible"] == "mc_bible_verse"


def test_the_rhyme_books_sign_has_no_play_button(db_file):
    # changed: the rhyme book's sign used to have ▶ PLAY for the verse
    at = start_app()
    start_new_game(at)
    choose(at, "inspect:rhyme_book", screen="picture")
    assert "play:mc_bible_verse" not in picture(at)["enabled"]
    sign = picture(at)["svg"]
    sign = sign[sign.index('data-overlay="inspect-rhyme_book"'):sign.index("<!-- end sign -->", sign.index('data-overlay="inspect-rhyme_book"'))]
    assert 'data-action="play:' not in sign and "♪ SONG" not in sign


def test_round_2_plays_the_verse(db_file):
    # changed: Bible finishes after Meyhem went first ("bible_finishes", was "rap_round_2")
    save_game(db_file, GameState(current_scene="station", inventory=["rhyme_book", "service_key"], rap_battle="meyhem_went_first"))
    at = start_app()
    choose(at, "resume")
    act(at, "bible_finishes")
    assert picture(at)["audio"]["src"] == "app/static/audio/mc_bible_verse.mp3"


def test_no_verse_when_round_2_is_turned_down(db_file):
    # changed: without his book Bible no longer gets turned down; he chokes, and his verse never plays
    at = resume_at(db_file, "station", ["service_key"])
    act(at, "bible_first")
    audio = picture(at)["audio"]
    assert audio is None or audio["src"] != "app/static/audio/mc_bible_verse.mp3"


def test_the_page_plays_sound_and_has_a_sound_switch():
    assert "new Audio()" in APP
    assert "sound-toggle" in APP and "localStorage" in APP
