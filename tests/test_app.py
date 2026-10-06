from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game
from logic import LOCKED_STATION_MESSAGE

APP_FILE = str(Path(__file__).parent.parent / "app.py")


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def start_app():
    """A fresh AppTest is a fresh app process: no session state carries over."""
    return AppTest.from_file(APP_FILE, default_timeout=10).run()


def click(at, key):
    at.button(key=key).click().run()
    assert not at.exception


def button_keys(at):
    return [button.key for button in at.button]


def test_no_resume_without_save(db_file):
    at = start_app()
    assert "new_game" in button_keys(at)
    assert "resume" not in button_keys(at)


def test_rejected_action_leaves_save_unchanged(db_file):
    # Done when 1 / A1
    at = start_app()
    click(at, "new_game")
    click(at, "go_block")
    saved_before = load_game(db_file)

    click(at, "enter_station")

    assert any(LOCKED_STATION_MESSAGE in w.value for w in at.warning)
    assert at.session_state["game"].current_scene == "block"
    assert at.session_state["game"].inventory == []
    assert load_game(db_file) == saved_before


def test_restart_resumes_progress(db_file):
    # Done when 4 / A4
    at = start_app()
    click(at, "new_game")
    click(at, "go_record_shop")
    click(at, "take_service_key")
    click(at, "go_block")

    restarted = start_app()
    assert "resume" in button_keys(restarted)
    assert "new_game" not in button_keys(restarted)  # restart confirmation comes with A6
    click(restarted, "resume")

    assert restarted.session_state["game"].current_scene == "block"
    assert restarted.session_state["game"].inventory == ["service_key"]
    assert "enter_station" in button_keys(restarted)

    click(restarted, "go_hq")
    click(restarted, "go_record_shop")
    assert "take_service_key" not in button_keys(restarted)

    click(restarted, "go_block")
    click(restarted, "enter_station")
    assert restarted.session_state["game"].current_scene == "station"
