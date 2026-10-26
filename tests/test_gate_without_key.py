"""Trying the gate without Rico's key: Reekz wishes they'd taken it, and back on the block Bible
says he was right. Being turned down at the gate changes nothing and saves nothing."""

from pathlib import Path

import pytest

from db import load_game, save_game
from logic import SCENES, GameState, apply_action, conversation, new_game, said_when_turned_down
from tests.apphelpers import act, choose, picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
GATE = (ROOT / "assets" / "scenes" / "gate.svg").read_text()
BLOCK = (ROOT / "assets" / "scenes" / "block.svg").read_text()
REEKZ = ("reekz", "WE REALLY SHOULD HAVE TAKEN THE KEY FROM RICO'S!")
BIBLE = ("bible", "REEKZ WAS RIGHT. LET'S GET THAT KEY FROM RICO'S!")


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
    return [s for s in picture(at)["show"] if s.startswith(("talk-", "back-", "locked-", "after-"))]


def bubble_in(svg, overlay):
    bubble = svg[svg.index(f'data-overlay="{overlay}"'):]
    return bubble[:bubble.index("</g>")]


# --- the rules ---

def test_reekz_wishes_they_had_taken_the_key():
    state = play(new_game(), "go_block", "go_gate")
    assert said_when_turned_down(state, "enter_station") == [REEKZ]


def test_bible_says_reekz_was_right_back_on_the_block():
    state = play(new_game(), "go_block", "go_gate", "go_block")
    assert conversation(state, tried="enter_station") == ("after", [BIBLE])
    assert conversation(state) == ("back", [])  # without having just tried: quiet, as before


# --- the pictures ---

def test_the_gate_has_reekz_bubble():
    bubble = bubble_in(GATE, "locked-0")
    assert "REEKZ" in bubble and 'data-action="next"' in bubble
    for word in REEKZ[1].split():
        assert word in bubble


def test_the_block_has_bibles_bubble():
    bubble = bubble_in(BLOCK, "after-0")
    assert "MC BIBLE" in bubble and 'data-action="next"' in bubble
    for word in BIBLE[1].split():
        assert word in bubble


# --- in the app ---

def at_the_gate(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    act(at, "go_gate")
    return at


def test_turned_down_at_the_gate_reekz_speaks_and_nothing_is_saved(db_file):
    at = at_the_gate(db_file)
    saved = load_game(db_file)
    act(at, "enter_station")
    shown = picture(at)["show"]
    assert "rejected-enter_station" in shown and "locked-0" in shown
    assert load_game(db_file) == saved
    assert at.session_state["game"] == saved
    choose(at, "next", screen="picture")  # the next click puts the sign and the bubble away
    assert "locked-0" not in picture(at)["show"] and "rejected-enter_station" not in picture(at)["show"]
    assert at.session_state["game"].current_scene == "gate"


def test_back_on_the_block_bible_says_reekz_was_right(db_file):
    at = at_the_gate(db_file)
    act(at, "enter_station")
    act(at, "go_block")
    assert bubbles(at) == ["after-0"]
    choose(at, "next", screen="picture")
    assert bubbles(at) == []
    act(at, "go_record_shop")  # later returns without the key: quiet again
    choose(at, "enter", screen="picture")
    act(at, "go_block")
    assert bubbles(at) == []


def test_just_going_back_from_the_gate_is_quiet(db_file):
    at = at_the_gate(db_file)
    act(at, "go_block")
    assert bubbles(at) == []


def test_with_the_key_the_gate_opens_and_reekz_says_nothing(db_file):
    save_game(db_file, GameState(current_scene="gate", inventory=["service_key"], left_scenes=["hq", "block"]))
    at = start_app()
    choose(at, "resume")
    act(at, "enter_station")
    assert at.session_state["game"].current_scene == "station"
    assert "locked-0" not in (picture(at) or {"show": []})["show"]
