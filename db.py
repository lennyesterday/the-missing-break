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
        " inventory TEXT NOT NULL,"
        " ending TEXT)"
    )
    # saves from before endings were remembered have no "ending" column yet
    columns = [row[1] for row in conn.execute("PRAGMA table_info(save)")]
    if "ending" not in columns:
        conn.execute("ALTER TABLE save ADD COLUMN ending TEXT")
    # ... and saves from before the rap battle's order mattered have no "rap_battle" column
    if "rap_battle" not in columns:
        conn.execute("ALTER TABLE save ADD COLUMN rap_battle TEXT")
    # ... and saves from before the plot twist have no "practiced" column
    if "practiced" not in columns:
        conn.execute("ALTER TABLE save ADD COLUMN practiced INTEGER NOT NULL DEFAULT 0")
    # ... and from before Grandmaster Flash: no money, nobody stuck, nobody met him
    for column in ("money", "stuck", "met_flash"):
        if column not in columns:
            conn.execute(f"ALTER TABLE save ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0")
    # ... and from before coming back mattered: no place left yet
    if "left_scenes" not in columns:
        conn.execute("ALTER TABLE save ADD COLUMN left_scenes TEXT NOT NULL DEFAULT '[]'")
    return conn


def save_game(path, state: GameState) -> None:
    with closing(_connect(path)) as conn, conn:
        conn.execute(
            "INSERT INTO save (id, current_scene, inventory, ending, rap_battle, practiced, money, stuck, met_flash,"
            " left_scenes) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(id) DO UPDATE SET"
            " current_scene = excluded.current_scene, inventory = excluded.inventory, ending = excluded.ending,"
            " rap_battle = excluded.rap_battle, practiced = excluded.practiced, money = excluded.money,"
            " stuck = excluded.stuck, met_flash = excluded.met_flash, left_scenes = excluded.left_scenes",
            (state.current_scene, json.dumps(state.inventory), state.ending, state.rap_battle, int(state.practiced),
             state.money, int(state.stuck), int(state.met_flash), json.dumps(state.left_scenes)),
        )


def load_game(path) -> GameState | None:
    with closing(_connect(path)) as conn:
        row = conn.execute("SELECT current_scene, inventory, ending, rap_battle, practiced, money, stuck, met_flash,"
                           " left_scenes FROM save WHERE id = 1").fetchone()
    if row is None:
        return None
    return GameState(current_scene=row[0], inventory=json.loads(row[1]), ending=row[2], rap_battle=row[3],
                     practiced=bool(row[4]), money=row[5], stuck=bool(row[6]), met_flash=bool(row[7]),
                     left_scenes=json.loads(row[8]))


def has_save(path) -> bool:
    return load_game(path) is not None
