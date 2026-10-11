"""The helicopter (coffee grinder), the footwork move of the cypher battle: squatting low on his
right leg, hands on the floor, his left leg straight out sweeps all the way round him, twice;
his right foot hops over it when it passes underneath, his hands lift when it passes in front.

changed: it replaces the 6-step, which the product owner took out ("the moves are still off")."""

import math

from art import cypher
from logic import CYPHER_MOVES, RIVAL_SETS


def sweep():
    return cypher._move("helicopter")


def around_support(f):
    """Where the sweeping foot is, as an angle round the support foot (degrees)."""
    (fx, _, fz), (sx, _, sz) = f["foot_l"], f["foot_r"]
    return math.degrees(math.atan2(fz - sz, fx - sx)) % 360


def test_it_replaces_the_6_step():
    assert "helicopter" in CYPHER_MOVES and "six_step" not in CYPHER_MOVES
    assert CYPHER_MOVES["helicopter"]["label"] == "HELICOPTER"
    assert all("six_step" not in s for s in RIVAL_SETS)


def test_it_starts_and_ends_down_on_his_hands():
    # changed: it starts and ends in the helicopter itself (low on his support leg, hands down),
    # not in a crouch: the next move goes straight on from there
    frames = sweep()
    assert frames[0] == frames[-1]
    assert frames[0]["hand_l"][1] < 8 and frames[0]["hand_r"][1] < 8          # hands on the floor
    assert (frames[0]["hip_l"][1] + frames[0]["hip_r"][1]) / 2 < 40              # down low


def test_the_leg_sweeps_all_the_way_round_and_stays_straight():
    frames = sweep()
    angles = {int(around_support(f) // 45) % 8 for f in frames}
    assert angles == set(range(8))                         # every direction round him
    swept = [f for f in frames if math.dist(f["foot_l"], f["hip_l"]) > 60]
    assert len(swept) > len(frames) / 2                    # most of the time the leg is out straight


def test_the_support_foot_hops_over_the_leg():
    # the leg passes under his support foot when it is out on the far (right) side of it
    frames = sweep()
    passing = [f for f in frames if min(around_support(f), 360 - around_support(f)) < 15
               and math.dist(f["foot_l"], f["hip_l"]) > 60]
    assert passing and all(f["foot_r"][1] > 12 for f in passing)   # in the air while it goes under


def test_the_hands_lift_when_the_leg_passes_in_front():
    frames = sweep()
    in_front = [f for f in frames if f["foot_l"][2] > 30]
    assert in_front and max(f["hand_l"][1] for f in in_front) > 20
