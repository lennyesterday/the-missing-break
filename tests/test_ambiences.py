"""Background sounds everywhere, made like the basement's (art/ambience.py, from scratch, no
copyright): the walks between places (the street), the block, Rico's Record Shop, the corner
store and Grandmaster Flash's realm. Each one a seamless loop, quieter than music."""

import wave
from pathlib import Path

import numpy as np
import pytest

from db import save_game
from logic import INTRO_MUSIC, SCENES, SONGS, GameState
from tests.apphelpers import choose, picture, start_app

ROOT = Path(__file__).parent.parent
SOUNDS = {"block": "block_ambience", "record_shop": "record_shop_ambience", "corner_store": "corner_store_ambience",
          "flash": "flash_ambience", "gate": "station_gate_ambience"}  # changed: the gate has its own (no footsteps)


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def samples(song):
    with wave.open(str(ROOT / "static" / SONGS[song]["file"])) as w:
        rate = w.getframerate()
        return rate, np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768


@pytest.mark.parametrize("scene, song", SOUNDS.items())
def test_each_place_has_its_own_background_sound(scene, song):
    assert SCENES[scene]["ambience"] == song


@pytest.mark.parametrize("song", sorted(set(SOUNDS.values())))
def test_the_sounds_are_made_here_and_loop(song):
    rate, a = samples(song)
    assert 25 <= len(a) / rate <= 45                       # a loop of half a minute or so
    assert np.sqrt(np.mean(a ** 2)) > 0.02                 # there is something to hear
    # the end runs into the start without a jump (no click where it loops round)
    step = np.abs(np.diff(a)).max()
    assert abs(a[0] - a[-1]) <= 2 * step
    assert SONGS[song].get("volume", 0.45) < SONGS[INTRO_MUSIC]["volume"]  # in the background


@pytest.mark.parametrize("song", sorted(set(SOUNDS.values())))
def test_they_are_all_different(song):
    _, a = samples(song)
    for other in set(SOUNDS.values()) - {song}:
        _, b = samples(other)
        assert not np.array_equal(a[:2000], b[:2000]), other


def test_how_they_are_made():
    text = (ROOT / "art" / "ambience.py").read_text()
    for name in ("street", "block", "record_shop", "corner_store", "flash"):
        assert f"def {name}_samples" in text, name


@pytest.mark.parametrize("scene, song", [(s, v) for s, v in SOUNDS.items() if s != "gate"])
def test_they_play_in_their_place(db_file, scene, song):
    save_game(db_file, GameState(current_scene=scene, inventory=["service_key"], met_flash=True, stuck=True))
    at = start_app()
    choose(at, "resume")
    assert picture(at)["ambience"] == f"app/static/{SONGS[song]['file']}"


def test_the_walks_have_the_street(db_file):
    save_game(db_file, GameState(current_scene="hq"))
    at = start_app()
    choose(at, "resume")
    choose(at, "go_block", screen="picture")              # the walk to the block
    assert at.session_state["walk"] and picture(at)["ambience"] == f"app/static/{SONGS['street_ambience']['file']}"
