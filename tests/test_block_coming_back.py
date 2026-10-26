"""Coming back to the block: the crew doesn't find the Sopranos' trail all over again. With Rico's
key they head for the station; without it they stay quiet (and the gate stays shut)."""

from pathlib import Path

import pytest

from db import load_game, save_game
from logic import LOCKED_STATION_MESSAGE, SCENES, GameState, apply_action, conversation, new_game
from tests.apphelpers import act, choose, picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
BLOCK = (ROOT / "assets" / "scenes" / "block.svg").read_text()


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def play(state, *action_ids):
    for action_id in action_ids:
        result = apply_action(state, action_id)
        assert result.accepted, f"{action_id} was rejected: {result.message}"
        state = result.state
    return state


def bubbles(at):
    return [s for s in picture(at)["show"] if s.startswith(("talk-", "back-"))]


# --- the rules ---

def test_the_first_time_on_the_block_is_the_first_conversation():
    assert conversation(play(new_game(), "go_block")) == ("talk", SCENES["block"]["dialogue"])


def test_back_from_rico_with_the_key_they_head_for_the_station():
    state = play(new_game(), "go_block", "go_record_shop", "take_service_key", "go_block")
    kind, lines = conversation(state)
    assert kind == "back" and lines == SCENES["block"]["dialogue_back"]["lines"]
    assert "STATION" in " ".join(text for _, text in lines)


def test_back_from_rico_without_the_key_they_stay_quiet():
    state = play(new_game(), "go_block", "go_record_shop", "go_block")
    assert conversation(state) == ("back", [])


def test_without_the_key_the_gate_still_doesnt_open():
    state = play(new_game(), "go_block", "go_record_shop", "go_block", "go_gate")
    result = apply_action(state, "enter_station")
    assert not result.accepted and result.message == LOCKED_STATION_MESSAGE
    assert result.state == state


def test_with_the_record_back_they_stay_quiet():
    state = GameState(current_scene="block", inventory=["service_key", "vinyl"], left_scenes=["hq", "block"])
    assert conversation(state) == ("back", [])


def test_the_basement_still_reminds_them_of_rico():
    state = play(new_game(), "go_block", "go_hq")
    assert conversation(state) == ("back", SCENES["hq"]["dialogue_back"]["lines"])


# --- the picture ---

def test_the_block_has_bubbles_for_coming_back():
    for i, (speaker, text) in enumerate(SCENES["block"]["dialogue_back"]["lines"]):
        bubble = BLOCK[BLOCK.index(f'data-overlay="back-{i}"'):]
        bubble = bubble[:bubble.index("</g>")]
        assert 'data-action="next"' in bubble
        for word in text.replace('"', "&quot;").split():
            assert word in bubble, (speaker, word)


def test_block_ricos_with_the_key_block_in_the_app(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    assert bubbles(at) == ["talk-0"]
    act(at, "go_record_shop")
    choose(at, "enter", screen="picture")  # ENTER RICO'S
    act(at, "take_service_key")
    act(at, "go_block")
    assert bubbles(at) == ["back-0"]
    choose(at, "next", screen="picture")
    assert bubbles(at) == ["back-1"]
    choose(at, "next", screen="picture")
    assert bubbles(at) == []


def test_block_ricos_without_the_key_block_in_the_app(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    act(at, "go_record_shop")
    choose(at, "enter", screen="picture")
    act(at, "go_block")
    assert bubbles(at) == []
    assert picture(at)["voice"] is None


def test_after_a_restart_with_the_key_it_is_still_the_new_conversation(db_file):
    save_game(db_file, GameState(current_scene="record_shop", inventory=["service_key"], left_scenes=["hq", "block"]))
    at = start_app()
    choose(at, "resume")
    act(at, "go_block")
    assert bubbles(at) == ["back-0"]
    assert load_game(db_file).current_scene == "block"


def test_coming_back_with_the_key_is_spoken(db_file):
    save_game(db_file, GameState(current_scene="record_shop", inventory=["service_key"], left_scenes=["hq", "block"]))
    at = start_app()
    choose(at, "resume")
    act(at, "go_block")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/block/back/00_portals.mp3"
    choose(at, "next", screen="picture")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/block/back/01_needle.mp3"
