from pathlib import Path

import pytest

from tests.apphelpers import act, click, offered, picture, shows_picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def shown_walk(at):
    return at.session_state["walk"] if "walk" in at.session_state else None


def test_pictures_are_drawn_inline_so_they_animate(db_file):
    # st.image shows an SVG as a still picture in the app: the walk did not move. Pictures
    # go through the svg_screen component instead, like the home screen.
    at = start_app()
    start_new_game(at)
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(at, "go_record_shop")

    assert len(at.get("image")) == 0
    assert shows_picture(at, "walk-block-record-shop")


def test_walk_file_for_hq_to_record_shop_exists():
    assert (ROOT / "assets" / "walks" / "block__record_shop.svg").is_file()


def test_moving_from_the_block_to_record_shop_shows_the_walk(db_file):
    # Done when 4: the crew walks from HQ to Rico's, then the record shop is shown
    at = start_app()
    start_new_game(at)  # START, then LET'S GO after the story intro
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block

    act(at, "go_record_shop")

    assert shown_walk(at) == "assets/walks/block__record_shop.svg"
    assert at.session_state["game"].current_scene == "record_shop"
    # changed: the walk ends at Rico's door; ENTER RICO'S is the only thing to do, then the
    # inside of the shop is shown with the key in the drawer
    assert picture(at)["enabled"] == ["enter"]
    act(at, "enter")
    assert shows_picture(at, "scene-record-shop")
    assert "take_service_key" in offered(at)


def test_rejected_action_shows_no_walk(db_file):
    # Done when 4: a rejected move is not a move
    at = start_app()
    start_new_game(at)  # START, then LET'S GO after the story intro
    act(at, "go_block")
    act(at, "go_gate")  # changed: the crew walks to the station gate first (the gate is its own place now)

    act(at, "enter_station")

    assert shown_walk(at) is None
    assert at.session_state["game"].current_scene == "gate"


def test_route_without_walk_file_still_works(db_file):
    # Done when 5: a missing transition file does not crash the app
    # changed: the basement -> block route has a walk now; block -> Disco Fever still has none
    at = start_app()
    start_new_game(at)  # START, then LET'S GO after the story intro
    act(at, "go_block")

    act(at, "go_battle")

    assert shown_walk(at) is None
    assert at.session_state["game"].current_scene == "battle"


def test_walk_is_gone_after_the_next_action(db_file):
    at = start_app()
    start_new_game(at)  # START, then LET'S GO after the story intro
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(at, "go_record_shop")
    act(at, "enter")  # changed: the walk ends at the door, ENTER RICO'S leads inside

    act(at, "take_service_key")

    assert shown_walk(at) is None
    assert at.session_state["game"].inventory == ["service_key"]
