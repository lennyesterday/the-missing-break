"""The breaking moves done properly. One body with fixed bone lengths (arms and legs never
stretch or shrink, knees and elbows bend the right way), never through the floor. Every move
goes straight on from where the last one ended: no squatting down in between."""

import math

import pytest

from art import cypher
from logic import CYPHER_BASES, CYPHER_MOVES

BONES = [("hip_l", "kn_l", cypher.THIGH), ("kn_l", "foot_l", cypher.SHIN), ("hip_r", "kn_r", cypher.THIGH),
         ("kn_r", "foot_r", cypher.SHIN), ("sh_l", "el_l", cypher.UPPER_ARM), ("el_l", "hand_l", cypher.FOREARM),
         ("sh_r", "el_r", cypher.UPPER_ARM), ("el_r", "hand_r", cypher.FOREARM)]
CLIPS = [(b, m) for b in CYPHER_BASES for m in CYPHER_MOVES]


def secs(frames):
    return (len(frames) - 1) / cypher.FPS


@pytest.mark.parametrize("base, move", CLIPS)
def test_arms_and_legs_keep_their_length(base, move):
    for f in cypher._from(base, move):
        for a, b, length in BONES:
            assert abs(math.dist(f[a], f[b]) - length) < 0.6, (a, b)


@pytest.mark.parametrize("base, move", CLIPS)
def test_nothing_goes_through_the_floor(base, move):
    for f in cypher._from(base, move):
        assert all(y > -0.5 for _, y, _ in f.values())


@pytest.mark.parametrize("base, move", CLIPS)
def test_no_squat_in_between_moves_go_straight_on(base, move):
    clip, own = cypher._from(base, move), cypher._move(move)
    lead = secs(clip) - secs(own)
    assert lead <= 0.8                                     # a quick flow from one into the next
    assert clip[0] == cypher.solve(cypher.EXIT[base])       # from exactly where he was
    assert clip[-1] == cypher.solve(cypher.EXIT[cypher.next_base_of(move)])


def test_every_move_ends_in_its_own_pose():
    ends = [cypher.solve(cypher.EXIT[b]) for b in CYPHER_BASES]
    for i, a in enumerate(ends):
        for b in ends[i + 1:]:
            assert a != b                                   # (not all in the same crouch)


def test_the_headspin_is_on_his_head_with_the_legs_up_and_spins():
    frames = cypher._move("headspin")
    spinning = frames[len(frames) // 3: 2 * len(frames) // 3]
    for f in spinning:
        assert f["head"][1] < 16 and min(f["foot_l"][1], f["foot_r"][1]) > 110
    assert cypher.HEADSPIN_TURNS >= 3
    pushes = [f for f in frames if f["hand_l"][1] < 6 and f["head"][1] < 16]
    assert pushes                                           # his hands push off the floor to start the spin


def test_the_1990_is_a_handstand_on_one_hand_that_turns():
    frames = cypher._move("nineteen_ninety")
    hand = frames[len(frames) // 2]["hand_r"]
    for f in frames[len(frames) // 4: 3 * len(frames) // 4]:
        assert f["hand_r"][1] < 4 and math.dist(f["hand_r"], hand) < 3      # the support hand stays put
        assert min(f["foot_l"][1], f["foot_r"][1]) > 130                     # legs straight up
        assert f["hand_l"][1] > 30                                           # the other hand off the floor


def test_the_freeze_hits_and_holds():
    frames = cypher._move("freeze")
    hold = frames[-int(1.0 * cypher.FPS):]
    for f in hold:
        for n in f:
            assert math.dist(f[n], hold[0][n]) < 3            # held still (only breathing)
    assert secs(frames) - 1.0 < 0.6                          # it snaps in


def test_toprock_steps_cross_in_front():
    frames = cypher._move("toprock")
    assert max(f["foot_r"][2] for f in frames) > 15 and min(f["foot_r"][0] for f in frames) < 0   # across, in front
    assert max(f["foot_l"][2] for f in frames) > 15 and max(f["foot_l"][0] for f in frames) > 0


def test_seen_from_a_bit_above_and_from_the_side():
    assert math.radians(18) <= cypher.CAMERA_PITCH <= math.radians(35)
    assert abs(cypher.CAMERA_YAW) >= math.radians(15)       # a three-quarter view: the floor moves read
    assert cypher.SCALE >= 0.85                             # bigger, so you see what he does
