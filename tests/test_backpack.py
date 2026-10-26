"""The crew's backpack: a 🎒 button in every scene picture and walk opens what the crew carries."""

import pytest

from db import load_game, save_game
from logic import ITEMS, GameState
from tests.apphelpers import act, choose, home_screen, picture, start_app, start_new_game


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def resume_at(db_file, state):
    save_game(db_file, state)
    at = start_app()
    choose(at, "resume")
    return at


def test_an_empty_backpack_in_the_basement(db_file):
    at = start_app()
    start_new_game(at)
    assert picture(at)["backpack"] == {"items": [], "cash": "$0.00"}


def test_taking_the_rhyme_book_puts_it_in_the_backpack(db_file):
    at = start_app()
    start_new_game(at)
    choose(at, "inspect:rhyme_book", screen="picture")
    choose(at, "take_rhyme_book", screen="picture")
    items = picture(at)["backpack"]["items"]
    assert [item["id"] for item in items] == ["rhyme_book"]
    assert items[0]["name"] == ITEMS["rhyme_book"]
    assert items[0]["icon"]


def test_the_backpack_keeps_the_order_and_shows_the_cash(db_file):
    at = resume_at(db_file, GameState(current_scene="block", inventory=["service_key", "rhyme_book"], money=1250))
    backpack = picture(at)["backpack"]
    assert [item["id"] for item in backpack["items"]] == ["service_key", "rhyme_book"]
    assert backpack["cash"] == "$12.50"


def test_every_item_has_an_icon(db_file):
    at = resume_at(db_file, GameState(current_scene="block", inventory=list(ITEMS)))
    assert all(item["icon"] for item in picture(at)["backpack"]["items"])


def test_the_backpack_comes_along_on_a_walk(db_file):
    at = resume_at(db_file, GameState(current_scene="block", inventory=["service_key"]))
    act(at, "go_record_shop")  # the walk to Rico's waits for ENTER
    assert at.session_state["walk"]
    assert [item["id"] for item in picture(at)["backpack"]["items"]] == ["service_key"]


def test_no_backpack_on_the_home_screen(db_file):
    at = start_app()
    assert home_screen(at).get("backpack") is None


def test_the_sidebar_shows_no_inventory(db_file):
    at = resume_at(db_file, GameState(current_scene="block", inventory=["service_key"]))
    assert len(at.sidebar) == 0


def test_the_backpack_is_not_a_move(db_file):
    at = resume_at(db_file, GameState(current_scene="block", inventory=["service_key"]))
    saved = load_game(db_file)
    at.run()
    assert load_game(db_file) == saved
    assert at.session_state["game"] == saved

