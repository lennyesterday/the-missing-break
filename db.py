"""SQLite storage: load and save progress."""

import json
import os
import sqlite3
from contextlib import closing

from logic import GameState

DEFAULT_DB_PATH = "game.db"


def db_path() -> str:
    """The save file. Tests point MISSING_BREAK_DB at a temporary file."""
    return os.environ.get("MISSING_BREAK_DB", DEFAULT_DB_PATH)


def _connect(path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS save ("
        " id INTEGER PRIMARY KEY CHECK (id = 1),"
        " current_scene TEXT NOT NULL,"
        " inventory TEXT NOT NULL)"
    )
    return conn


def save_game(path, state: GameState) -> None:
    with closing(_connect(path)) as conn, conn:
        conn.execute(
            "INSERT INTO save (id, current_scene, inventory) VALUES (1, ?, ?)"
            " ON CONFLICT(id) DO UPDATE SET"
            " current_scene = excluded.current_scene, inventory = excluded.inventory",
            (state.current_scene, json.dumps(state.inventory)),
        )


def load_game(path) -> GameState | None:
    with closing(_connect(path)) as conn:
        row = conn.execute("SELECT current_scene, inventory FROM save WHERE id = 1").fetchone()
    if row is None:
        return None
    return GameState(current_scene=row[0], inventory=json.loads(row[1]))


def has_save(path) -> bool:
    return load_game(path) is not None
