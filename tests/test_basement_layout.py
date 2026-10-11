"""The basement's layout: buttons never lie on things the player can click, and the sound system
stands clear of the records on the floor."""

import math
import re
from pathlib import Path

from art.build import BASEMENT_SLEEVES

ROOT = Path(__file__).parent.parent
HQ = (ROOT / "assets" / "scenes" / "hq.svg").read_text()


def sleeve_box(x, y, rot, half=25):
    """A sleeve is a 50x50 square turned by rot degrees: the box around it."""
    r = half * (abs(math.cos(math.radians(rot))) + abs(math.sin(math.radians(rot))))
    return (x - r, y - r, x + r, y + r)


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


SLEEVES = {record: sleeve_box(x, y, rot) for record, _, _, x, y, rot in BASEMENT_SLEEVES}
THINGS = dict(SLEEVES, rhyme_book=sleeve_box(517, 300, -10, half=24), empty_sleeve=sleeve_box(368, 386, -6, half=23))


def way_out_box():
    button = HQ[HQ.index('data-action="go_block"'):]
    x, y, w, h = map(float, re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', button).groups())
    return (x, y, x + w, y + h)


def soundsystem_box():
    # the cabinets are drawn from (10, 140) to (150, 376), then scaled down standing on their foot
    foot, scale = map(float, re.search(r'id="soundsystem" transform="translate\(10 ([\d.]+)\) scale\(([\d.]+)\)', HQ).groups())
    return (10, foot + scale * (140 - 376), 10 + scale * 140, foot)


def test_no_button_lies_on_a_thing_to_click():
    button = way_out_box()
    for thing, box in THINGS.items():
        assert not overlap(button, box), thing


def test_no_two_sleeves_lie_on_each_other():
    names = list(SLEEVES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert not overlap(SLEEVES[a], SLEEVES[b]), (a, b)


def test_the_soundsystem_is_smaller_and_stands_clear_of_the_records():
    box = soundsystem_box()
    assert box[2] - box[0] <= 72  # changed: it was 98 wide and stood on The Mexican and Apache
    for thing, sleeve in THINGS.items():
        assert not overlap(box, sleeve), thing
