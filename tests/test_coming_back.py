"""Coming back to the basement: the crew doesn't find the break-in all over again. Before it has
Rico's key it reminds itself to go to Rico's; after that it says nothing."""

import sqlite3
from pathlib import Path

import pytest

from db import load_game, save_game
from logic import SCENES, GameState, apply_action, conversation, new_game
from tests.apphelpers import act, choose, picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
HQ = (ROOT / "assets" / "scenes" / "hq.svg").read_text()


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

def test_a_new_game_starts_with_the_first_conversation():
    assert conversation(new_game()) == ("talk", SCENES["hq"]["dialogue"])


def test_leaving_a_place_is_remembered():
    state = play(new_game(), "go_block")
    assert state.left_scenes == ["hq"]
    assert play(state, "go_hq", "go_block").left_scenes == ["hq", "block"]  # each place once


def test_a_rejected_action_remembers_nothing():
    state = play(new_game(), "go_block", "go_gate")
    result = apply_action(state, "enter_station")  # no key
    assert not result.accepted and result.state.left_scenes == state.left_scenes


def test_coming_back_without_the_key_reminds_them_of_rico():
    kind, lines = conversation(play(new_game(), "go_block", "go_hq"))
    assert kind == "back" and lines == SCENES["hq"]["dialogue_back"]["lines"]
    said = " ".join(text for _, text in lines)
    assert "RICO'S" in said and "SOPRANOS" in said


def test_coming_back_with_the_key_they_say_nothing():
    state = GameState(current_scene="hq", inventory=["service_key"], left_scenes=["hq"])
    assert conversation(state) == ("back", [])


def test_other_places_keep_their_conversation():
    # changed: the block has its own return conversation now (specs/story-line-fixes-2.md), so Rico's
    state = play(new_game(), "go_block", "go_record_shop", "go_block", "go_record_shop")
    assert conversation(state) == ("talk", SCENES["record_shop"]["dialogue"])


# --- saving ---

def test_left_scenes_are_saved_and_loaded(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, GameState(current_scene="block", left_scenes=["hq"]))
    assert load_game(path).left_scenes == ["hq"]


def test_a_save_from_before_has_left_nothing(tmp_path):
    path = tmp_path / "game.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE save (id INTEGER PRIMARY KEY CHECK (id = 1), current_scene TEXT NOT NULL, inventory TEXT NOT NULL)")
    conn.execute("INSERT INTO save VALUES (1, 'block', '[]')")
    conn.commit()
    conn.close()
    assert load_game(path).left_scenes == []


# --- the picture ---

def test_the_basement_has_bubbles_for_the_return_conversation():
    for i, (speaker, text) in enumerate(SCENES["hq"]["dialogue_back"]["lines"]):
        bubble = HQ[HQ.index(f'data-overlay="back-{i}"'):]
        bubble = bubble[:bubble.index("</g>")]
        assert 'data-action="next"' in bubble
        for word in text.replace('"', "&quot;").split():
            assert word in bubble, (speaker, word)


def test_basement_block_basement_shows_the_return_conversation(db_file):
    at = start_app()
    start_new_game(at)
    assert bubbles(at) == ["talk-0"]
    act(at, "go_block")
    act(at, "go_hq")
    assert bubbles(at) == ["back-0"]
    # changed: the return lines are recorded now (they were silent at first)
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/hq/back/00_needle.mp3"
    first = picture(at)["voice"]
    choose(at, "next", screen="picture")
    assert bubbles(at) == ["back-1"]
    # changed: Meyhem's line went to Bible (specs/remove-meyhem.md): silent until it is recorded
    assert picture(at)["voice"] is None
    choose(at, "next", screen="picture")
    assert bubbles(at) == []
    # ... and the next time they come back, the reminder comes again, spoken again (a new voice id)
    act(at, "go_block")
    act(at, "go_hq")
    assert bubbles(at) == ["back-0"]
    again = picture(at)["voice"]
    assert again["src"] == first["src"] and again["id"] != first["id"]


def test_after_a_restart_it_is_still_the_return_conversation(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    restarted = start_app()  # a fresh app: no session state
    choose(restarted, "resume")
    act(restarted, "go_hq")
    assert bubbles(restarted) == ["back-0"]


def test_coming_back_with_the_key_shows_no_bubble(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"], left_scenes=["hq"]))
    at = start_app()
    choose(at, "resume")
    act(at, "go_hq")
    assert bubbles(at) == []


def test_every_return_line_is_recorded():
    for i, (speaker, _) in enumerate(SCENES["hq"]["dialogue_back"]["lines"]):
        from tests.test_voices import recorded
        assert recorded("hq/back", i, speaker), (i, speaker)  # changed: Bible's line (was Meyhem's) isn't recorded yet
