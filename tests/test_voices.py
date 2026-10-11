"""The crew's voices: each speech bubble plays its line, if a recording exists
(static/audio/voices/<scene>/<number>_<speaker>.mp3)."""

from pathlib import Path

import pytest

from logic import SCENES
from tests.apphelpers import act, choose, picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
VOICES = ROOT / "static" / "audio" / "voices"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def test_every_recording_belongs_to_a_line_and_its_speaker():
    for scene_dir in VOICES.iterdir():
        dialogue = SCENES[scene_dir.name]["dialogue"]
        for f in scene_dir.glob("*.mp3"):
            number, speaker = f.stem.split("_", 1)
            assert dialogue[int(number)][0] == speaker, f.name


def test_needle_and_bible_are_recorded():
    assert (VOICES / "hq" / "00_needle.mp3").is_file()
    assert (VOICES / "hq" / "01_bible.mp3").is_file()


def test_needle_speaks_when_the_basement_appears(db_file):
    at = start_app()
    start_new_game(at)
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/hq/00_needle.mp3"


def test_the_click_to_the_next_bubble_plays_bible(db_file):
    at = start_app()
    start_new_game(at)
    first = picture(at)["voice"]
    choose(at, "next", screen="picture")
    voice = picture(at)["voice"]
    assert voice["src"] == "app/static/audio/voices/hq/01_bible.mp3" and voice["id"] != first["id"]


def test_a_line_without_a_recording_is_silent(db_file):
    # changed: every basement line is recorded now, so this checks a scene without recordings
    from db import save_game
    from logic import GameState
    save_game(db_file, GameState(current_scene="block", inventory=[]))
    at = start_app()
    choose(at, "resume")
    assert picture(at)["voice"] is None


def test_no_voice_after_leaving(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    assert picture(at)["voice"] is None or "voices/hq" not in picture(at)["voice"]["src"]


def test_the_page_plays_voices_and_lowers_the_background_meanwhile():
    app = (ROOT / "app.py").read_text()
    assert "data.voice" in app and "ended" in app


def test_the_whole_basement_conversation_is_recorded():
    lines = SCENES["hq"]["dialogue"]
    for i, (speaker, _) in enumerate(lines):
        assert (VOICES / "hq" / f"{i:02d}_{speaker}.mp3").is_file(), (i, speaker)


def test_every_line_is_spoken_in_turn(db_file):
    at = start_app()
    start_new_game(at)
    heard = []
    for i, (speaker, _) in enumerate(SCENES["hq"]["dialogue"]):
        heard.append(picture(at)["voice"]["src"])
        choose(at, "next", screen="picture")
    assert heard == [f"app/static/audio/voices/hq/{i:02d}_{s}.mp3" for i, (s, _) in enumerate(SCENES["hq"]["dialogue"])]
    assert picture(at)["voice"] is None  # the conversation is over


def test_the_texts_match_the_recordings():
    texts = [line for _, line in SCENES["hq"]["dialogue"]]
    assert texts[2] == "YO! THAT SHIT IS CRAZY, DAWG. THE CRATE IS EMPTY!"  # changed: edited by the product owner
    assert texts[4] == "THEY WENT OVER OUR PIECE. THAT'S DISRESPECTFUL, SON!"
    assert texts[5] == 'THEY TOOK "THINK ABOUT IT", MY SECRET BREAK FOR THE FINAL!'
    assert texts[7] == "FIRST I NEED MY RHYME BOOK TO WRITE A DISS FOR KRETE. IT'S ON THE COUCH."
