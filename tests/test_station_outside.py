"""The old 149th St station from outside, and the walks there and back. From the block the crew
walks to the station (with SKIP); at the gate they stand in front of the old station house; back
to the block they walk the same street the other way, from the gate and from the station (out
of the open gate). It sounds like the other places: the street, a train on the el whenever it
passes in the picture, the key, the padlock, the chain and the gate when it opens."""

import json
import re
import wave
from pathlib import Path

import numpy as np
import pytest

from art import ambience, build
from db import load_game, save_game
from logic import SCENES, SONGS, GameState
from tests.apphelpers import choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
WALKS = ROOT / "assets" / "walks"
TO_GATE, GATE_BACK, STATION_BACK = WALKS / "block__gate.svg", WALKS / "gate__block.svg", WALKS / "station__block.svg"
UNLOCK = WALKS / "gate__station.svg"
GATE = ROOT / "assets" / "scenes" / "gate.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def at_the(db_file, scene, inventory=()):
    save_game(db_file, GameState(current_scene=scene, inventory=list(inventory)))
    at = start_app()
    choose(at, "resume")
    return at


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def wav(rel):
    with wave.open(str(ROOT / rel)) as w:
        rate = w.getframerate()
        return rate, np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768


def loudness(a, rate, t, width=0.08):
    s = int(t * rate)
    part_ = a[max(0, s - int(0.01 * rate)):s + int(width * rate)]
    return float(np.sqrt(np.mean(part_ ** 2))) if len(part_) else 0.0


# --- the walks ---------------------------------------------------------------------------------

@pytest.mark.parametrize("scene, action, inventory, walk, arrives", [
    ("block", "go_gate", (), "assets/walks/block__gate.svg", "scene-gate"),
    ("gate", "go_block", (), "assets/walks/gate__block.svg", "scene-block"),
    ("station", "go_block", ("service_key",), "assets/walks/station__block.svg", "scene-block"),
])
def test_the_crew_walks_there_and_back(db_file, scene, action, inventory, walk, arrives):
    at = at_the(db_file, scene, inventory)
    choose(at, action, screen="picture")
    assert at.session_state["walk"] == walk
    assert picture(at)["enabled"] == ["enter"]
    assert load_game(db_file).current_scene != scene       # the move is saved when they set off
    choose(at, "enter", screen="picture")                  # on by itself at the end, or SKIP
    assert shows_picture(at, arrives)


@pytest.mark.parametrize("path", [TO_GATE, GATE_BACK, STATION_BACK])
def test_each_walk_goes_on_by_itself_or_with_skip(path):
    svg = path.read_text()
    end = float(re.search(r'<svg[^>]*data-auto-delay="([\d.]+)"', svg).group(1))
    assert re.search(r'<svg[^>]*data-auto-action="enter"', svg) and end >= 4
    skip = svg[svg.index('aria-label="Skip the walk"') - 120:]
    assert 'data-action="enter"' in skip[:200] and "SKIP" in skip


def test_the_gate_opening_can_be_skipped_too():
    svg = UNLOCK.read_text()
    skip = svg[svg.index('aria-label="Skip the walk"') - 120:]
    assert 'data-action="enter"' in skip[:200] and "SKIP" in skip


def test_the_walk_there_follows_the_sopranos_tags():
    svg = TO_GATE.read_text()
    for member in ("Fantastic Needle", "MC Bible", "Reekz", "Portals (denim"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert f"<!-- {member}" in svg, member
    assert 'attributeName="transform" type="translate" from="0 0"' in svg   # they walk in
    trail = part(svg, 'id="sopranos-trail"', "<!-- end sopranos-trail -->")
    assert len(re.findall(r'class="tag"[^>]*>(Sopranos|Krete|SF|Krete 77)', trail)) >= 5


def test_back_the_same_street_facing_the_other_way():
    street = lambda svg: svg[svg.index("<!-- the street to the station -->"):svg.index("<!-- end station street -->")]
    there = TO_GATE.read_text()
    for path in (GATE_BACK, STATION_BACK):
        back = path.read_text()
        assert street(back) == street(there), path
        assert 'id="crew-walking-back" transform="translate(800 0) scale(-1 1)"' in back
    assert "crew-walking-back" not in there


def test_out_of_the_station_the_gate_is_open():
    # they come up the stairs: the gate stays folded open, the chain and the padlock are gone
    svg = STATION_BACK.read_text()
    entrance = part(svg, 'id="station-entrance"', "<!-- end station-entrance -->")
    assert 'id="padlock"' not in entrance and 'id="chain"' not in entrance
    assert 'id="scissor-gate" class="open"' in entrance
    shut = part(GATE_BACK.read_text(), 'id="station-entrance"', "<!-- end station-entrance -->")
    assert 'id="padlock"' in shut                           # (from the gate it's still chained)


def test_at_the_gate_they_are_already_there():
    # changed: the crew used to walk in at the gate itself; that's the walk now (with SKIP), so
    # at the gate they stand still and the ways on are there at once
    svg = GATE.read_text()
    assert 'type="translate" from="0 0"' not in svg
    assert 'begin="4s"' not in svg
    assert 'data-action="enter_station"' in svg and 'data-action="go_block"' in svg


@pytest.mark.parametrize("path", [TO_GATE, GATE_BACK, STATION_BACK, UNLOCK, GATE])
def test_bible_with_or_without_his_book(path):
    svg = path.read_text()
    assert re.search(r'data-overlay="has-rhyme_book[" ]', svg) and re.search(r'data-overlay="lacks-rhyme_book[" ]', svg)


@pytest.mark.parametrize("asset, make", [
    ("assets/walks/block__gate.svg", build.walk_block_to_gate), ("assets/walks/gate__block.svg", build.walk_gate_to_block),
    ("assets/walks/station__block.svg", build.walk_station_to_block), ("assets/walks/gate__station.svg", build.walk_gate_to_station),
    ("assets/scenes/gate.svg", build.gate_scene)])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()


# --- the station, nicer ------------------------------------------------------------------------

def test_an_old_station_house_with_its_name_in_mosaic():
    entrance = part(GATE.read_text(), 'id="station-entrance"', "<!-- end station-entrance -->")
    for piece_ in ('id="headhouse"', 'id="station-roof"', 'id="station-arch"', 'id="stairs"', 'id="scissor-gate"',
                   'id="globe-left"', 'id="globe-right"'):
        assert piece_ in entrance, piece_
    assert "149 ST" in entrance and "GRAND CONCOURSE" in entrance and "STATION CLOSED" in entrance
    assert "data-action" not in entrance


def test_one_globe_flickers_the_stairs_glow():
    entrance = part(GATE.read_text(), 'id="station-entrance"', "<!-- end station-entrance -->")
    right = part(entrance, 'id="globe-right"', "</g>")
    assert 'attributeName="opacity"' in right and "keyTimes" in right       # flickering, broken
    stairs = part(entrance, 'id="stairs"', "<!-- end stairs -->")
    assert "<animate" in stairs                                            # a light far down below


def test_the_street_is_alive():
    svg = GATE.read_text()
    for thing in ('id="steam"', 'id="newspaper"', 'id="pigeons"', 'id="rat"'):
        assert thing in svg, thing
        assert "<animate" in part(svg, thing, f"<!-- end {thing[4:-1]} -->"), thing


# --- the sounds --------------------------------------------------------------------------------

def test_the_gate_has_its_own_background_sound():
    assert SCENES["gate"]["ambience"] == "station_gate_ambience"
    assert "station_gate" in ambience.AMBIENCES
    rate, a = wav(f"static/{SONGS['station_gate_ambience']['file']}")
    assert 25 <= len(a) / rate <= 45 and np.sqrt(np.mean(a ** 2)) > 0.02
    assert abs(a[0] - a[-1]) <= 2 * np.abs(np.diff(a)).max()   # it loops without a click


def test_no_footsteps_while_they_stand_at_the_gate():
    text = (ROOT / "art" / "ambience.py").read_text()
    code = text[text.index("def station_gate_samples"):text.index("\ndef ", text.index("def station_gate_samples"))]
    assert "step" not in code and "_street(m" in code and "_underground" in code


@pytest.mark.parametrize("path", [TO_GATE, GATE_BACK, STATION_BACK, UNLOCK, GATE])
def test_the_train_sounds_whenever_it_passes(path):
    svg = path.read_text()
    passing, every, at = build.STATION_TRAIN
    m = re.search(r'values="820 0;820 0;-900 0;-900 0" keyTimes="0;([\d.]+);([\d.]+);1" dur="([\d.]+)s"', svg)
    assert m and float(m.group(3)) == every
    assert float(m.group(1)) * every == pytest.approx(at, abs=0.01)
    assert (float(m.group(2)) - float(m.group(1))) * every == pytest.approx(passing, abs=0.01)
    cues = json.loads(re.search(r"data-cues='([^']+)'", svg).group(1))
    train = next(c for c in cues if c["src"].endswith("block/train.wav"))
    assert train["every"] == every and train["on"] == [[at, at + passing]]


def test_the_gate_opening_sounds():
    svg = UNLOCK.read_text()
    cues = json.loads(re.search(r"data-cues='([^']+)'", svg).group(1))
    cue = next(c for c in cues if c["src"].endswith("station/unlock.wav"))
    rate, a = wav(cue["src"].removeprefix("app/"))
    start = cue["on"][0][0]
    assert abs(cue["on"][0][1] - start - len(a) / rate) < 0.05
    quiet = loudness(a, rate, 0.0, 0.03)
    for t in build.UNLOCK_SOUNDS.values():                 # the key, the padlock, the chain, the gate
        assert loudness(a, rate, t - start) > 3 * quiet + 0.02, t
