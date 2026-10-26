"""Dialogue update (specs/dialogue-update.md): the new recordings are spoken: the station, the
block after the win, the basement after Needle's try, the walk through the portal and Flash's realm."""

import re
from pathlib import Path

import pytest

from db import save_game
from logic import SCENES, WALK_LINES, GameState
from tests.apphelpers import act, choose, picture, start_app

ROOT = Path(__file__).parent.parent
VOICES = ROOT / "static" / "audio" / "voices"
WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]
LEFT = ["hq", "block", "record_shop", "gate", "station"]


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def heard(at, folder, lines):
    """Click through the bubbles: what's spoken with each one."""
    srcs = []
    for _ in lines:
        voice = picture(at)["voice"]
        srcs.append(voice and voice["src"])
        choose(at, "next", screen="picture")
    return srcs


def spoken(folder, lines):
    return [f"app/static/audio/voices/{folder}/{i:02d}_{speaker}.mp3" for i, (speaker, _) in enumerate(lines)]


@pytest.mark.parametrize("folder, lines", [
    ("station", SCENES["station"]["dialogue"]),
    ("block/won", SCENES["block"]["dialogue_won"]["lines"]),
    ("hq/stuck", SCENES["hq"]["dialogue_stuck"]["lines"]),
    ("flash", SCENES["flash"]["dialogue"]),
])
def test_every_line_is_recorded(folder, lines):
    for i, (speaker, _) in enumerate(lines):
        assert (VOICES / folder / f"{i:02d}_{speaker}.mp3").is_file(), (folder, i, speaker)


def test_the_walk_line_is_recorded():
    assert WALK_LINES["hq__flash"] == [("reekz", "YOU DID IT!", WALK_LINES["hq__flash"][0][2])]
    assert (VOICES / "walks" / "hq__flash" / "00_reekz.mp3").is_file()


def test_the_basement_after_the_try_is_spoken(db_file):
    save_game(db_file, GameState(current_scene="hq", inventory=WITH_RECORD, rap_battle="won", stuck=True, left_scenes=LEFT))
    at = start_app()
    choose(at, "resume")
    lines = SCENES["hq"]["dialogue_stuck"]["lines"]
    assert heard(at, "hq/stuck", lines) == spoken("hq/stuck", lines)


def test_back_on_the_block_after_the_win_is_spoken(db_file):
    save_game(db_file, GameState(current_scene="station", inventory=WITH_RECORD, rap_battle="won", left_scenes=LEFT[:-1]))
    at = start_app()
    choose(at, "resume")
    act(at, "go_block")
    lines = SCENES["block"]["dialogue_won"]["lines"]
    assert heard(at, "block/won", lines) == spoken("block/won", lines)


def test_flash_speaks(db_file):
    save_game(db_file, GameState(current_scene="hq", inventory=WITH_RECORD, rap_battle="won", stuck=True, left_scenes=LEFT))
    at = start_app()
    choose(at, "resume")
    act(at, "go_flash")  # the walk through the portal, then Flash's realm
    lines = SCENES["flash"]["dialogue"]
    assert heard(at, "flash", lines) == spoken("flash", lines)


def test_reekz_says_it_in_the_walk_when_his_bubble_shows(db_file):
    save_game(db_file, GameState(current_scene="hq", inventory=WITH_RECORD, rap_battle="won", stuck=True, left_scenes=LEFT))
    at = start_app()
    choose(at, "resume")
    choose(at, "go_flash", screen="picture")
    voice = picture(at)["voice"]
    _, _, at_secs = WALK_LINES["hq__flash"][0]
    assert voice["src"] == "app/static/audio/voices/walks/hq__flash/00_reekz.mp3"
    assert voice["delay"] == at_secs
    walk = (ROOT / "assets" / "walks" / "hq__flash.svg").read_text()
    bubble = walk[walk.index("<title>Reekz: YOU DID IT!</title>"):][:200]
    assert f'begin="{at_secs:.2f}s"' in bubble                           # the bubble shows right then


def test_the_page_can_wait_before_a_voice():
    app = (ROOT / "app.py").read_text()
    assert re.search(r"data\.voice\.delay", app)
