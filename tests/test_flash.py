"""The Grandmaster Flash layer. With the record back Needle tries to practice but can't catch
the break; Portals opens a portal to Grandmaster Flash, the guru: "the secret lies in the
crayon". After meeting him the b-boy cypher shows up on the block (a win: $10), the corner store
(always open, but nothing to do without money) sells crayons, and with crayons Needle can mark
the break and practice."""

import sqlite3

import pytest

from db import load_game, save_game
from logic import (CRAYON_MESSAGE, ITEMS, NO_MONEY_MESSAGE, SCENES, GameState, apply_action, available_actions,
                   new_game)

WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]


def ids(state):
    return [a["id"] for a in available_actions(state)]


def play(state, *steps):
    for step in steps:
        result = apply_action(state, step)
        assert result.accepted, (step, result.message)
        state = result.state
    return state


# --- Needle can't catch the break: Portals opens a portal to Flash ---

def test_with_the_record_needle_tries_to_practice_first():
    state = GameState(current_scene="hq", inventory=WITH_RECORD)
    assert "try_practice" in ids(state) and "go_flash" not in ids(state) and "practice" not in ids(state)
    result = apply_action(state, "try_practice")
    assert result.accepted and "Grandmaster Flash" in result.message
    assert result.state.stuck is True and "try_practice" not in ids(result.state)
    assert "go_flash" in ids(result.state)                       # Portals can open the portal now


def test_through_the_portal_to_grandmaster_flash():
    state = play(GameState(current_scene="hq", inventory=WITH_RECORD), "try_practice", "go_flash")
    assert state.current_scene == "flash" and state.met_flash is True
    assert "go_hq" in ids(state)                                  # back through the portal
    lines = " ".join(line for _, line in SCENES["flash"]["dialogue"])
    assert "CRAYON" in lines
    assert {who for who, _ in SCENES["flash"]["dialogue"]} >= {"flash", "needle"}


def test_practice_needs_the_crayons_flash_talked_about():
    met = GameState(current_scene="hq", inventory=WITH_RECORD, stuck=True, met_flash=True)
    assert "practice" in ids(met)
    result = apply_action(met, "practice")
    assert not result.accepted and result.message == CRAYON_MESSAGE
    assert result.state == met                                    # turned down: nothing changes
    with_crayons = GameState(current_scene="hq", inventory=WITH_RECORD + ["crayons"], stuck=True, met_flash=True)
    assert apply_action(with_crayons, "practice").state.practiced is True


# --- the cypher shows up after Flash, and pays ---

def test_the_cypher_is_there_only_after_meeting_flash():
    assert SCENES["block"]["things"]["cypher"]["when_flag"] == "met_flash"
    assert "win_cypher" not in ids(GameState(current_scene="block"))
    assert "win_cypher" in ids(GameState(current_scene="block", met_flash=True))


def test_winning_the_cypher_pays_ten_dollars_each_time():
    state = GameState(current_scene="block", met_flash=True)
    state = play(state, "win_cypher")
    assert state.money == 1000 and "$10" in apply_action(GameState(current_scene="block", met_flash=True), "win_cypher").message
    assert play(state, "win_cypher").money == 2000


def test_winning_the_cypher_is_not_a_button():
    action = next(a for a in SCENES["block"]["actions"] if a["id"] == "win_cypher")
    assert action["by_app"] is True                               # the app gives it after a won battle


# --- the corner store: always open, nothing without money ---

def test_the_corner_store_is_always_open():
    assert "go_store" in ids(GameState(current_scene="block"))
    state = play(GameState(current_scene="block"), "go_store")
    assert state.current_scene == "corner_store" and "go_block" in ids(state)


@pytest.mark.parametrize("item", ["crayons", "chips", "soda", "candy"])
def test_without_money_nothing_happens(item):
    state = GameState(current_scene="corner_store")
    result = apply_action(state, f"buy_{item}")
    assert not result.accepted and result.message == NO_MONEY_MESSAGE
    assert result.state == state


def test_buying_crayons_and_snacks():
    state = GameState(current_scene="corner_store", money=1000)
    prices = {a["id"]: a["costs"] for a in SCENES["corner_store"]["actions"] if "costs" in a}
    assert prices == {"buy_crayons": 100, "buy_chips": 50, "buy_soda": 25, "buy_candy": 10}
    state = play(state, "buy_crayons", "buy_chips")
    assert state.money == 850 and state.inventory == ["crayons", "chips"]
    assert "buy_crayons" not in ids(state)                        # one box is enough
    assert ITEMS["crayons"] and ITEMS["chips"]


def test_not_enough_money_for_it():
    state = GameState(current_scene="corner_store", money=30)
    assert not apply_action(state, "buy_chips").accepted
    assert apply_action(state, "buy_soda").state.money == 5


# --- saving ---

def test_money_and_the_flash_story_are_saved(tmp_path):
    path = tmp_path / "game.db"
    state = GameState(current_scene="corner_store", inventory=["crayons"], money=850, stuck=True, met_flash=True)
    save_game(path, state)
    assert load_game(path) == state


def test_older_saves_load_with_no_money_and_no_flash(tmp_path):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE save (id INTEGER PRIMARY KEY CHECK (id = 1), current_scene TEXT NOT NULL,"
                     " inventory TEXT NOT NULL, ending TEXT, rap_battle TEXT, practiced INTEGER NOT NULL DEFAULT 0)")
        conn.execute("INSERT INTO save VALUES (1, 'block', '[]', NULL, NULL, 0)")
    state = load_game(path)
    assert state.money == 0 and state.stuck is False and state.met_flash is False


# --- the whole way ---

def test_the_whole_way_to_the_legends():
    state = play(new_game(), "take_rhyme_book", "go_block", "go_record_shop", "take_service_key", "go_block",
                 "go_gate", "enter_station", "rap_battle", "go_block", "go_hq",  # changed: Bible raps alone (specs/remove-meyhem.md)
                 "try_practice", "go_flash", "go_hq", "go_block", "win_cypher", "go_store", "buy_crayons",
                 "buy_soda", "go_block", "go_hq", "practice", "go_block", "go_battle", "start_battle")
    assert state.ending == "ending_legends"
