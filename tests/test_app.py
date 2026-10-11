import pytest

from db import load_game, save_game
from logic import LOCKED_STATION_MESSAGE, GameState
from tests.apphelpers import act, button_keys, choose, click, home_screen, intro_screen, offered, picture, start_app, start_new_game


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def test_no_resume_without_save(db_file):
    # Changed with the graffiti home screen: Start and Resume are on the train now.
    # Without a save, Resume is shown but cannot be used.
    at = start_app()
    assert "start" in home_screen(at)["enabled"]
    assert "resume" not in home_screen(at)["enabled"]


def test_rejected_action_leaves_save_unchanged(db_file):
    # Done when 1 / A1
    at = start_app()
    start_new_game(at)  # START, then LET'S GO after the story intro
    act(at, "go_block")
    act(at, "go_gate")  # changed: the crew walks to the station gate first (the gate is its own place now)
    saved_before = load_game(db_file)

    act(at, "enter_station")

    # changed: the block is played in its picture, so the message is a sign in the picture
    # (it used to be a Streamlit warning under it); the checks are the same
    assert "rejected-enter_station" in picture(at)["show"]
    sign = picture(at)["svg"]
    sign = sign[sign.index('data-overlay="rejected-enter_station"'):]
    assert LOCKED_STATION_MESSAGE.upper() in sign[:sign.index("<!-- end rejected -->")]
    assert at.session_state["game"].current_scene == "gate"
    assert at.session_state["game"].inventory == []
    assert load_game(db_file) == saved_before


def test_restart_resumes_progress(db_file):
    # Done when 4 / A4
    # Changed with the graffiti home screen: this used to assert that "New game" is hidden
    # when a save exists. Start is now always offered and asks for confirmation (PT01, A6),
    # which the tests below check.
    at = start_app()
    start_new_game(at)  # START, then LET'S GO after the story intro
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(at, "go_record_shop")
    act(at, "enter")  # changed: the walk ends at the door, ENTER RICO'S leads inside
    act(at, "take_service_key")
    act(at, "go_block")

    restarted = start_app()
    assert "resume" in home_screen(restarted)["enabled"]
    choose(restarted, "resume")

    assert restarted.session_state["game"].current_scene == "block"
    assert restarted.session_state["game"].inventory == ["service_key"]
    assert "go_gate" in offered(restarted)  # changed: the crew walks to the station gate first (the gate is its own place now)

    act(restarted, "go_record_shop")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(restarted, "enter")  # changed: the walk ends at the door, ENTER RICO'S leads inside
    assert "take_service_key" not in offered(restarted)

    act(restarted, "go_block")
    act(restarted, "go_gate")  # changed: the crew walks to the station gate first (the gate is its own place now)
    act(restarted, "enter_station")
    assert restarted.session_state["game"].current_scene == "station"


def test_start_without_save_begins_a_new_game(db_file):
    at = start_app()
    choose(at, "start")

    assert at.session_state["game"].current_scene == "hq"
    assert at.session_state["game"].inventory == []
    assert load_game(db_file) == GameState(current_scene="hq", inventory=[])


def test_start_with_save_asks_for_confirmation(db_file):
    # PT01: starting over must ask before replacing existing progress.
    # Changed: the question is now a graffiti sign on the home screen, not Streamlit buttons below it.
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()

    choose(at, "start")

    assert "game" not in at.session_state
    assert home_screen(at)["show"] == ["confirm-restart"]
    assert home_screen(at)["enabled"] == ["restart_yes", "restart_no"]  # the train waits meanwhile
    assert load_game(db_file) == GameState(current_scene="block", inventory=["service_key"])


def test_cancel_restart_keeps_progress(db_file):
    # A6: cancel a restart and verify progress is retained
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()
    choose(at, "start")

    choose(at, "restart_no")  # changed: CANCEL on the graffiti sign

    assert home_screen(at)["show"] == []
    assert load_game(db_file) == GameState(current_scene="block", inventory=["service_key"])
    choose(at, "resume")
    assert at.session_state["game"].current_scene == "block"
    assert at.session_state["game"].inventory == ["service_key"]


def test_confirm_restart_resets_progress(db_file):
    # A6: confirm a restart and verify the opening scene and empty inventory are restored
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()
    choose(at, "start")

    choose(at, "restart_yes")  # changed: YES, START OVER on the graffiti sign

    assert at.session_state["game"].current_scene == "hq"
    assert at.session_state["game"].inventory == []
    assert load_game(db_file) == GameState(current_scene="hq", inventory=[])


def test_resume_without_save_does_nothing(db_file):
    at = start_app()
    choose(at, "resume")

    assert "game" not in at.session_state
    assert home_screen(at) is not None


def test_menu_does_nothing_yet(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()

    choose(at, "menu")

    assert "game" not in at.session_state
    assert home_screen(at) is not None
    assert load_game(db_file) == GameState(current_scene="block", inventory=["service_key"])


def test_start_shows_the_story_intro(db_file):
    # After START, Portals sprays the story onto the wall before the game begins
    at = start_app()
    choose(at, "start")

    assert intro_screen(at) is not None
    assert intro_screen(at)["enabled"] == ["go", "skip"]  # changed: SKIP was added
    assert home_screen(at) is None
    assert "go_block" not in offered(at)  # the scene's actions come after the intro
    assert load_game(db_file) == GameState(current_scene="hq", inventory=[])


def test_lets_go_ends_the_intro_in_hq(db_file):
    at = start_app()
    choose(at, "start")

    choose(at, "go", screen="intro")
    choose(at, "arrive", screen="escape")  # changed: LET'S GO first shows Portals' escape through the portal

    assert intro_screen(at) is None
    assert at.session_state["game"].current_scene == "hq"
    assert "go_block" in offered(at)  # changed: the basement only leads to the block; Rico's is reached from the block


def test_confirmed_restart_also_shows_the_intro(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()
    choose(at, "start")
    choose(at, "restart_yes")

    assert intro_screen(at) is not None


def test_resume_skips_the_intro(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()
    choose(at, "resume")

    assert intro_screen(at) is None
    assert "go_gate" in offered(at)  # changed: the crew walks to the station gate first (the gate is its own place now)


def test_home_screen_has_no_text_or_buttons_below_it(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()
    choose(at, "start")  # even while asking to start over

    assert len(at.title) == 0
    assert len(at.markdown) == 0
    assert len(at.warning) == 0
    assert button_keys(at) == []


def test_train_buttons_do_nothing_while_asking(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=["service_key"]))
    at = start_app()
    choose(at, "start")

    choose(at, "resume")

    assert "game" not in at.session_state
    assert home_screen(at)["show"] == ["confirm-restart"]


def test_skip_jumps_to_the_end_of_the_intro(db_file):
    at = start_app()
    choose(at, "start")
    assert intro_screen(at)["seek_end"] is False

    choose(at, "skip", screen="intro")

    assert intro_screen(at) is not None  # still the intro, now at its end, so LET'S GO is there
    assert intro_screen(at)["seek_end"] is True
    assert "go" in intro_screen(at)["enabled"]
    choose(at, "go", screen="intro")
    choose(at, "arrive", screen="escape")  # changed: LET'S GO first shows Portals' escape through the portal
    assert intro_screen(at) is None
    assert at.session_state["game"].current_scene == "hq"


def test_a_new_intro_starts_from_the_beginning_again(db_file):
    at = start_app()
    choose(at, "start")
    choose(at, "skip", screen="intro")
    choose(at, "go", screen="intro")
    choose(at, "arrive", screen="escape")  # changed: LET'S GO first shows Portals' escape through the portal

    again = start_app()  # play again later: START, confirm, and the intro plays from the start
    choose(again, "start")
    choose(again, "restart_yes")
    assert intro_screen(again)["seek_end"] is False
