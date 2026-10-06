from db import has_save, load_game, save_game
from logic import GameState


def test_no_save_returns_none(tmp_path):
    path = tmp_path / "game.db"
    assert load_game(path) is None
    assert not has_save(path)


def test_save_and_load_roundtrip_after_reopen(tmp_path):
    # Part of A4: every call opens a fresh connection, like a restarted app.
    path = tmp_path / "game.db"
    save_game(path, GameState(current_scene="block", inventory=["service_key"]))

    loaded = load_game(path)

    assert has_save(path)
    assert loaded.current_scene == "block"
    assert loaded.inventory == ["service_key"]


def test_saving_again_overwrites_the_single_slot(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, GameState(current_scene="hq", inventory=[]))
    save_game(path, GameState(current_scene="station", inventory=["service_key"]))

    loaded = load_game(path)

    assert loaded.current_scene == "station"
    assert loaded.inventory == ["service_key"]
