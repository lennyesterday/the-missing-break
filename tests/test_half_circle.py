"""The battles: the crew doesn't stand in a line, they stand round the battle in a half circle,
like a cypher (the ones further back smaller and higher up, the ones at the sides nearer and
bigger). At the rap battle the GoodFellas are on one side of the mic, the Sopranos on the other;
the rapper walks out of the circle to the mic. At the breaking battle the GoodFellas and Kid
Cyclone's crew stand round the cardboard, and a crowd from the block watches behind them, from
the store's window and door too. And the figures everywhere have more detail."""

import re
from pathlib import Path

import pytest

from art import build, crew, cypher

ROOT = Path(__file__).parent.parent
STATION = ROOT / "assets" / "scenes" / "station.svg"
CLIPS = sorted((ROOT / "assets" / "cypher").glob("*.svg"))


def spots(svg):
    """Everyone standing in the circle: (x, feet, scale, who)."""
    return [(float(x), float(f), float(s), who) for x, f, s, who in
            re.findall(r'<g class="in-circle" data-x="([\d.]+)" data-feet="([\d.]+)" data-scale="([\d.]+)" data-who="([^"]+)"', svg)]


def is_half_circle(places, centre):
    """Further from the middle: nearer to us (lower, bigger). On both sides of the middle."""
    left = sorted((p for p in places if p[0] < centre), key=lambda p: -p[0])
    right = sorted((p for p in places if p[0] > centre), key=lambda p: p[0])
    assert len(left) >= 3 and len(right) >= 2, places
    for side in (left, right):
        for near, far in zip(side, side[1:]):            # going out from the middle ...
            assert far[1] > near[1], (near, far)          # ... they stand further forward
            assert far[2] > near[2], (near, far)          # ... and look bigger
    return True


# --- the rap battle ----------------------------------------------------------------------------

def test_at_the_rap_battle_they_stand_round_the_mic():
    places = spots(STATION.read_text())
    assert is_half_circle(places, centre=410)
    who = {p[3] for p in places}
    assert {"portals", "needle", "bible", "reekz"} <= who  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
    goodfellas = [p for p in places if p[3] in ("portals", "needle", "bible", "reekz")]
    sopranos = [p for p in places if p[3].startswith("sopranos")]
    assert all(p[0] < 410 for p in goodfellas) and len(sopranos) >= 2 and all(p[0] > 410 for p in sopranos)


def test_no_two_of_the_crew_on_one_line():
    goodfellas = [p for p in spots(STATION.read_text()) if p[3] in ("portals", "needle", "bible", "reekz")]  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
    assert len({p[1] for p in goodfellas}) == len(goodfellas)    # every one at his own depth


@pytest.mark.parametrize("who", ["bible", "bible_chokes"])  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
def test_the_rapper_walks_out_of_the_circle_to_the_mic(who):
    svg = STATION.read_text()
    performs = svg[svg.index(f'id="{who}-performs"'):svg.index(f"<!-- end {who}-performs -->")]
    walk = re.search(r'<animateTransform attributeName="transform" type="translate" values="([\d.]+) ([\d.]+);([\d.]+) ([\d.]+)"', performs)
    assert walk, who
    x0, f0, x1, f1 = map(float, walk.groups())
    spot = next(p for p in spots(svg) if p[3] == who.replace("_chokes", ""))
    assert (x0, f0) == (spot[0], spot[1]) and x1 > x0 and f1 > f0      # from his spot, forward to the mic
    assert re.search(r'type="scale" values="[\d.]+;1"', performs)        # coming nearer: bigger


def test_the_speech_bubbles_point_at_the_heads():
    places = {p[3]: p for p in spots(STATION.read_text())}
    for who, (_, _, (x, y)) in build.STATION_SPEAKERS.items():
        if who in places:
            px, feet, s, _ = places[who]
            assert abs(x - px) < 12 and abs(y - (feet - crew.HEAD_ABOVE_FEET * s)) < 12, who


# --- the breaking battle -----------------------------------------------------------------------

@pytest.mark.parametrize("clip", CLIPS, ids=lambda p: p.stem)
def test_at_the_breaking_battle_they_stand_round_the_cardboard(clip):
    places = spots(clip.read_text())
    assert is_half_circle(places, centre=cypher.FLOOR[0])
    who = {p[3] for p in places}
    assert {"portals", "needle", "bible"} <= who  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
    assert sum(w.startswith("bboy") for w in who) >= 4


@pytest.mark.parametrize("clip", CLIPS, ids=lambda p: p.stem)
def test_a_crowd_watches_the_breaking_battle(clip):
    svg = clip.read_text()
    assert svg.count('class="onlooker"') >= 14
    assert 'id="store-window-crowd"' in svg and 'id="store-door-crowd"' in svg
    assert svg.count('class="onlooker cheering"') >= 4                 # some throw their arms up


def test_onlookers_are_people_in_many_looks():
    people = "".join(crew.onlooker(100 + 30 * k, 360, crew.LOOKS[k % len(crew.LOOKS)], k) for k in range(10))
    assert people.count('class="onlooker"') == 10
    assert len(set(re.findall(r'fill="(#[0-9a-f]{6})"', people))) >= 12


# --- more detail -------------------------------------------------------------------------------

@pytest.mark.parametrize("figure", [crew.needle(100), crew.bible(100), crew.portals(100), crew.reekz(100)])
def test_the_figures_have_more_detail(figure):  # changed (no crew.meyhem): MC Meyhem left the crew
    for part in ('class="ear"', 'class="brow"', 'class="mouth"', 'class="sole"', 'class="shade"', 'class="belt"'):
        assert part in figure, part


def test_placing_someone_in_the_circle():
    placed = crew.placed(crew.needle(200), "needle", 200, 390, 0.9)
    assert placed.startswith('<g class="in-circle" data-x="200" data-feet="390" data-scale="0.9" data-who="needle"')
    assert f'translate(200 390) scale(0.9) translate(-200 -{crew.FEET_Y})' in placed
