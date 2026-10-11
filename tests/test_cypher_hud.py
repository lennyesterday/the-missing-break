"""The breaking battle's buttons don't cover the dance: they sit in a strip along the bottom,
under the cardboard; the dancer and the cardboard are above it. What's up next shows on its
button. And the moves look better: a neck, a toprock with a kick, a headspin with the legs
scissoring, a freeze that hits."""

import math
import re
from pathlib import Path

import pytest

from art import cypher
from logic import CYPHER_MOVES

ROOT = Path(__file__).parent.parent
CLIP = (ROOT / "assets" / "cypher" / "toprock_from_stand.svg").read_text()


def rect_of(svg, action):
    """The rect of a button (its first rect)."""
    i = svg.index(f'data-action="{action}"')
    x, y, w, h = map(float, re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg[i:]).groups())
    return x, y, w, h


@pytest.mark.parametrize("action", [f"move:{m}" for m in CYPHER_MOVES] + ["leave_cypher"])
def test_the_buttons_sit_in_the_strip_at_the_bottom(action):
    x, y, w, h = rect_of(CLIP, action)
    assert y >= cypher.HUD_TOP and y + h <= 450 and x >= 0 and x + w <= 800


def test_the_dance_is_above_the_strip():
    assert cypher.FLOOR[1] <= cypher.HUD_TOP - 12                  # his feet, and the shadow
    cardboard = CLIP[CLIP.index('id="cardboard"'):CLIP.index("</g>", CLIP.index('id="cardboard"'))]
    ys = [float(v) for v in re.findall(r'[ML]?\d+ (\d+)', re.search(r' d="([^"]+)"', cardboard).group(1))]
    assert max(ys) <= cypher.HUD_TOP


def test_the_question_and_up_next_stay_off_the_dance():
    choose = CLIP[CLIP.index('data-overlay="choose"'):CLIP.index("<!-- end choose -->")]
    for y in map(float, re.findall(r'<(?:rect|text)[^>]* y="([\d.]+)"', choose)):
        assert y >= cypher.HUD_TOP - 14, y                          # all down in the strip
    for move in CYPHER_MOVES:                                        # up next: on its own button
        queued = choose[choose.index(f'data-overlay="queued-{move}"'):]
        bx, by, bw, bh = rect_of(CLIP, f"move:{move}")
        qx = float(re.search(r'x="([\d.]+)"', queued).group(1))
        assert bx - 6 <= qx <= bx + bw, move


def test_he_has_a_neck():
    assert 'class="neck"' in CLIP[CLIP.index('id="reekz-3d"'):]


def test_toprock_has_a_kick():
    frames = cypher._move("toprock")
    assert any(f["foot_r"][2] > 30 and f["foot_r"][1] > 22 for f in frames) or \
        any(f["foot_l"][2] > 30 and f["foot_l"][1] > 22 for f in frames)


def test_the_legs_scissor_in_the_headspin():
    frames = cypher._move("headspin")
    spin = frames[len(frames) // 3:]
    spreads = [math.dist(f["foot_l"], f["foot_r"]) for f in spin]
    assert max(spreads) - min(spreads) > 30                          # they open and close as he spins


def test_the_freeze_hits_past_and_settles():
    frames = cypher._from("headspin", "freeze")
    final = frames[-1]
    lead = len(frames) - len(cypher._move("freeze"))
    near_end = frames[lead - 4:lead]                                  # just before it holds ...
    assert max(math.dist(f["foot_l"], final["foot_l"]) for f in near_end) > 4   # ... the legs go past
    assert frames[lead] == cypher.solve(cypher.ENTRY["freeze"])       # and settle into the freeze
