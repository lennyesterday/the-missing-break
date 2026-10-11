"""The cypher battle: Reekz against Kid Cyclone, up to 3 rounds. Each round Kid Cyclone goes
first, then the player picks Reekz's moves one after the other (TOPROCK, HELICOPTER, HEADSPIN,
1990, FREEZE; changed: the helicopter replaced the 6-step) until a freeze ends the set (or 4 moves). The crowd judges each round; two rounds win
the cypher. The moves are drawn in 3D from one skeleton and connect: every move starts in the
pose the one before ended in. Only for show: nothing is saved."""

import re
from pathlib import Path

import pytest

import logic
from db import load_game, save_game
from logic import (CYPHER_BASES, CYPHER_MOVES, RIVAL_SETS, GameState, cypher_clip, cypher_result, next_base, score_set)
from tests.apphelpers import choose, start_app, svg_screen

ROOT = Path(__file__).parent.parent
CLIPS = ROOT / "assets" / "cypher"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


# --- the rules ---

def test_the_moves():
    assert list(CYPHER_MOVES) == ["toprock", "helicopter", "headspin", "nineteen_ninety", "freeze"]
    assert [m["label"] for m in CYPHER_MOVES.values()] == ["TOPROCK", "HELICOPTER", "HEADSPIN", "1990", "FREEZE"]


def test_a_classic_set_flows():
    # toprock -> footwork -> power -> freeze: points, plus a flow bonus for every step up, a finish
    points, notes = score_set(["toprock", "helicopter", "headspin", "freeze"], earlier=[])
    assert points == 1 + (2 + 1) + (3 + 1) + (2 + 1)
    assert "flow" in notes and "finish" in notes


def test_the_same_move_twice_in_a_row_costs():
    points, notes = score_set(["headspin", "headspin", "freeze"], earlier=[])
    assert points == 3 + (3 - 2) + (2 + 1)
    assert "repeat" in notes


def test_moves_shown_in_an_earlier_round_count_less():
    fresh, _ = score_set(["toprock", "nineteen_ninety", "freeze"], earlier=[])
    seen, notes = score_set(["toprock", "nineteen_ninety", "freeze"], earlier=["toprock", "nineteen_ninety"])
    assert seen == fresh - 2 and "seen" in notes


def test_no_freeze_no_finish():
    points, notes = score_set(["toprock", "helicopter", "headspin", "nineteen_ninety"], earlier=[])
    assert points == 1 + 3 + 4 + 3 - 2
    assert "no_freeze" in notes and "finish" not in notes


def test_kid_cyclone_goes_by_the_same_rules():
    assert RIVAL_SETS[0] == ["toprock", "helicopter", "freeze"]
    assert len(RIVAL_SETS) == 3
    assert score_set(RIVAL_SETS[0], earlier=[])[0] == 7


@pytest.mark.parametrize("rounds, result", [
    ([(11, 7), (8, 6)], "won"),            # two rounds: the cypher is his
    ([(5, 7), (6, 6)], "lost"),            # a tie goes to Kid Cyclone, it's his block
    ([(11, 7), (5, 6)], None),             # one each: round 3 decides
    ([(11, 7), (5, 6), (9, 8)], "won"),
])
def test_two_rounds_win_the_cypher(rounds, result):
    assert cypher_result(rounds) == result


def test_moves_connect_through_their_poses():
    # changed: a move no longer goes back to one crouch for all floor moves; the next move goes
    # on from the pose this one ended in (standing after toprock); a freeze ends the set
    assert next_base("toprock") == "stand"
    for move in ("helicopter", "headspin", "nineteen_ninety", "freeze"):
        assert next_base(move) == move
    assert set(CYPHER_BASES) == {"stand", "helicopter", "headspin", "nineteen_ninety"}
    assert cypher_clip("headspin", "freeze") == "assets/cypher/freeze_from_headspin.svg"


# --- the 3D clips ---

def first_and_last_d(svg):
    """The first and last frame of the first limb of Reekz's 3D body."""
    body = svg[svg.index('id="reekz-3d"'):]
    values = re.search(r'<animate attributeName="d" values="([^"]+)"', body).group(1).split(";")
    return values[0], values[-1]


@pytest.mark.parametrize("move", list(CYPHER_MOVES))
@pytest.mark.parametrize("base", CYPHER_BASES)  # changed: from every pose a move can end in
def test_every_move_has_a_clip_from_each_pose(base, move):
    svg = (ROOT / cypher_clip(base, move)).read_text()
    assert 'id="reekz-3d"' in svg
    assert 'class="front"' in svg and 'class="back"' in svg and 'calcMode="discrete"' in svg  # 3D: limbs pass in front and behind
    assert re.search(r'<svg[^>]*data-auto-action="move_done"', svg)  # the page says when the move is over


def test_the_moves_actually_connect():
    # a clip starts exactly where every clip that ends in its pose stops
    ends = {}
    for move in CYPHER_MOVES:
        for base in CYPHER_BASES:  # changed: every base, not stand and crouch
            ends.setdefault(next_base(move), set()).add(first_and_last_d((ROOT / cypher_clip(base, move)).read_text())[1])
    for base in CYPHER_BASES:
        assert len(ends[base]) == 1, base  # every move that ends standing (or down) ends in the same pose
        for move in CYPHER_MOVES:
            start = first_and_last_d((ROOT / cypher_clip(base, move)).read_text())[0]
            assert start in ends[base], (base, move)
    # and Kid Cyclone's set ends with Reekz stepping in standing, where his first move starts
    for r in (1, 2, 3):
        rival = (CLIPS / f"rival_{r}.svg").read_text()
        assert first_and_last_d(rival)[1] in ends["stand"], r


@pytest.mark.parametrize("r", [1, 2, 3])
def test_kid_cyclone_has_a_set_each_round(r):
    svg = (CLIPS / f"rival_{r}.svg").read_text()
    assert 'id="rival-3d"' in svg
    assert re.search(r'<svg[^>]*data-auto-action="reekz_turn"', svg)
    assert f"ROUND {r}" in svg


def test_the_battle_signs():
    svg = (ROOT / cypher_clip("stand", "toprock")).read_text()
    choose_sign = svg[svg.index('data-overlay="choose"'):svg.index("<!-- end choose -->")]
    for move, info in CYPHER_MOVES.items():
        assert f'data-action="move:{move}"' in choose_sign and info["label"] in choose_sign
    for overlay in ("round-won", "round-lost", "cypher-won", "cypher-lost", "note-flow", "note-repeat", "note-seen",
                    "note-no_freeze", "note-finish", "reekz-score-11", "rival-score-7"):
        assert f'data-overlay="{overlay}"' in svg, overlay
    assert 'data-action="next_round"' in svg and 'data-action="leave_cypher"' in svg


def test_clips_match_their_source():
    from art import cypher
    assert (ROOT / cypher_clip("helicopter", "headspin")).read_text() == cypher.reekz_clip("helicopter", "headspin")  # changed: no crouch clips
    assert (CLIPS / "rival_2.svg").read_text() == cypher.rival_clip(2)


# --- in the app ---

def battle(db_file):
    # changed: the cypher only shows up after Needle has been to Grandmaster Flash
    save_game(db_file, GameState(current_scene="block", inventory=[], met_flash=True))
    at = start_app()
    choose(at, "resume")
    choose(at, "inspect:cypher", screen="picture")
    choose(at, "join:cypher", screen="picture")
    return at


def shown(at):
    return svg_screen(at, "cypher")


def play_set(at, moves):
    for move in moves:
        assert f"move:{move}" in shown(at)["enabled"], move
        choose(at, f"move:{move}", screen="cypher")
        choose(at, "move_done", screen="cypher")


def test_join_in_and_kid_cyclone_goes_first(db_file):
    at = battle(db_file)
    s = shown(at)
    assert s["file"] == "assets/cypher/rival_1.svg"
    assert {"reekz_turn", "leave_cypher"} <= set(s["enabled"])
    choose(at, "reekz_turn", screen="cypher")
    s = shown(at)
    assert "choose" in s["show"]
    assert {f"move:{m}" for m in CYPHER_MOVES} <= set(s["enabled"])


def test_each_pick_plays_the_move_from_where_he_is(db_file):
    at = battle(db_file)
    choose(at, "reekz_turn", screen="cypher")
    choose(at, "move:toprock", screen="cypher")
    assert shown(at)["file"] == "assets/cypher/toprock_from_stand.svg"
    # changed: the next move can already be picked while he does this one (it used to wait)
    assert shown(at)["enabled"][:1] == ["move_done"] and "choose" in shown(at)["show"]
    choose(at, "move_done", screen="cypher")
    choose(at, "move:helicopter", screen="cypher")
    assert shown(at)["file"] == "assets/cypher/helicopter_from_stand.svg"   # he drops down first
    choose(at, "move_done", screen="cypher")
    first = shown(at)["nonce"]
    choose(at, "move:headspin", screen="cypher")
    assert shown(at)["file"] == "assets/cypher/headspin_from_helicopter.svg"  # changed: straight out of the helicopter
    assert shown(at)["nonce"] != first                                     # every move plays from its start
    assert "did-0-toprock" in shown(at)["show"] and "did-1-helicopter" in shown(at)["show"]


def test_a_freeze_ends_the_set_and_the_crowd_judges(db_file):
    at = battle(db_file)
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["toprock", "helicopter", "headspin", "freeze"])
    s = shown(at)
    assert {"judge", "round-won", "reekz-score-11", "rival-score-7", "note-flow", "note-finish"} <= set(s["show"])
    assert "next_round" in s["enabled"]
    choose(at, "next_round", screen="cypher")
    assert shown(at)["file"] == "assets/cypher/rival_2.svg"


def test_winning_the_cypher(db_file):
    at = battle(db_file)
    saved = load_game(db_file)
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["toprock", "helicopter", "headspin", "freeze"])
    choose(at, "next_round", screen="cypher")
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["helicopter", "nineteen_ninety", "freeze"])
    s = shown(at)
    assert "cypher-won" in s["show"] and "next_round" not in s["enabled"]
    # changed: the winner wins $10 now (it used to be only for show); nothing else changes
    from dataclasses import replace
    assert load_game(db_file) == replace(saved, money=saved.money + 1000)


def test_losing_the_cypher(db_file):
    at = battle(db_file)
    for _ in range(2):
        choose(at, "reekz_turn", screen="cypher")
        play_set(at, ["toprock", "toprock", "toprock", "toprock"])
        if "next_round" in shown(at)["enabled"]:
            choose(at, "next_round", screen="cypher")
    s = shown(at)
    assert "cypher-lost" in s["show"] and "note-repeat" in s["show"] and "note-no_freeze" in s["show"]


def test_leaving_the_cypher_any_time(db_file):
    at = battle(db_file)
    choose(at, "leave_cypher", screen="cypher")
    assert shown(at) is None
    assert logic.SONGS  # (the music stops: see test_cypher.py)


# --- picking the next move while he still does this one: they flow straight into each other ---

def test_the_next_move_can_be_picked_ahead(db_file):
    at = battle(db_file)
    choose(at, "reekz_turn", screen="cypher")
    choose(at, "move:toprock", screen="cypher")
    assert {f"move:{m}" for m in CYPHER_MOVES} <= set(shown(at)["enabled"])  # live while he toprocks
    choose(at, "move:headspin", screen="cypher")
    s = shown(at)
    assert s["file"] == "assets/cypher/toprock_from_stand.svg"  # he finishes his toprock first
    assert "queued-headspin" in s["show"]
    choose(at, "move:nineteen_ninety", screen="cypher")        # a change of mind
    assert "queued-nineteen_ninety" in shown(at)["show"] and "queued-headspin" not in shown(at)["show"]
    nonce = shown(at)["nonce"]
    choose(at, "move_done", screen="cypher")                   # the toprock is over: straight into the 1990
    s = shown(at)
    assert s["file"] == "assets/cypher/nineteen_ninety_from_stand.svg"
    assert s["nonce"] != nonce and not any(n.startswith("queued-") for n in s["show"])
    assert "did-1-nineteen_ninety" in s["show"]


def test_without_a_pick_he_waits_in_his_pose(db_file):
    at = battle(db_file)
    choose(at, "reekz_turn", screen="cypher")
    choose(at, "move:toprock", screen="cypher")
    choose(at, "move_done", screen="cypher")
    s = shown(at)
    assert s["file"] == "assets/cypher/toprock_from_stand.svg" and "choose" in s["show"]
    assert "move_done" not in s["enabled"]


def test_nothing_to_pick_during_the_last_move_of_a_set(db_file):
    at = battle(db_file)
    choose(at, "reekz_turn", screen="cypher")
    choose(at, "move:freeze", screen="cypher")
    s = shown(at)
    assert "choose" not in s["show"] and not any(e.startswith("move:") for e in s["enabled"])


def test_the_page_shows_whats_up_next():
    svg = (ROOT / cypher_clip("stand", "toprock")).read_text()
    for move, info in CYPHER_MOVES.items():
        assert f'data-overlay="queued-{move}"' in svg and f"UP NEXT: {info['label']}" in svg
