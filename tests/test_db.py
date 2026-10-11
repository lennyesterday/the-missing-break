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


def test_an_ending_is_saved_and_loaded(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, GameState(current_scene="battle", inventory=["vinyl"], ending="ending_legends"))
    assert load_game(path) == GameState(current_scene="battle", inventory=["vinyl"], ending="ending_legends")


def test_a_save_from_before_endings_still_loads(tmp_path):
    # saves made before the ending was remembered have no "ending" column
    import sqlite3
    path = tmp_path / "game.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE save (id INTEGER PRIMARY KEY CHECK (id = 1), current_scene TEXT NOT NULL, inventory TEXT NOT NULL)")
    conn.execute("INSERT INTO save VALUES (1, 'block', '[\"service_key\"]')")
    conn.commit()
    conn.close()
    assert load_game(path) == GameState(current_scene="block", inventory=["service_key"], ending=None)
    save_game(path, GameState(current_scene="battle", inventory=[], ending="ending_static"))
    assert load_game(path).ending == "ending_static"
