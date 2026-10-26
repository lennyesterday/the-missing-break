"""The block: the basketball court with the Sopranos' fresh tags and the chained station gate."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import LOCKED_STATION_MESSAGE, SCENES, GameState
from tests.apphelpers import act, choose, picture, shows_picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
BLOCK = ROOT / "assets" / "scenes" / "block.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def test_the_basketball_court():
    svg = BLOCK.read_text()
    assert 'id="scene-block"' in svg
    # changed: the station is no longer on the block (the crew walks there); a corner store is there instead
    # (the basketball is Needle's now: he dunks it)
    for p in ('id="hoop"', 'id="court"', 'id="fence"', 'id="basketball"', 'id="sopranos-wall"', 'id="corner-store"'):
        assert p in svg
    assert 'id="station-entrance"' not in svg
    assert "the passing train" in svg


def test_the_wall_is_full_of_fresh_sopranos_tags():
    wall = part(BLOCK.read_text(), 'id="sopranos-wall"', "<!-- end sopranos-wall -->")
    assert len(re.findall(r'class="tag"[^>]*>(Sopranos|Krete|SF)', wall)) >= 5
    assert "SOPRANOS" in wall and "♛" in wall


def test_the_corner_store():
    # changed: the chained station gate moved to the station gate (test_walk_to_station.py);
    # the corner of the block is a bodega now, called CORNER STORE
    store = part(BLOCK.read_text(), 'id="corner-store"', "<!-- end corner-store -->")
    assert "CORNER STORE" in store and "OPEN" in store
    assert "data-action" not in store


def test_a_b_boy_cypher_in_front_of_the_corner_store():
    # changed: instead of random people in the front, a breaking crew cyphers in the background
    svg = BLOCK.read_text()
    assert "<!-- Bystander" not in svg
    cypher = part(svg, 'id="cypher"', "<!-- end cypher -->")
    assert cypher.count("<!-- B-boy") >= 4
    assert "<!-- B-boy (toprock" in cypher                     # one of them dances
    assert 'id="cardboard"' in cypher and 'id="cypher-boombox"' in cypher
    scale = float(re.search(r'id="cypher"[^>]*scale\(([\d.]+)\)', svg).group(1))
    assert scale <= 0.7                                          # smaller: in the background
    assert svg.index('id="cypher"') < svg.index("<!-- Fantastic Needle")  # drawn behind the crew


# changed: the crew used to shoot hoops on a loop; now the ball lies on the court, the player
# clicks it and picks DUNK or 3-POINTER, and then someone runs, takes the ball and goes for it

def test_the_ball_lies_on_the_court_and_can_be_clicked():
    svg = BLOCK.read_text()
    ball = part(svg, 'id="basketball"', "<!-- end basketball -->")
    assert 'data-action="inspect:basketball"' in ball
    assert 'data-overlay="!shooting"' in svg[svg.rindex("<g", 0, svg.index('<g id="basketball"')):][:40]
    sign = part(svg, 'data-overlay="inspect-basketball"', "<!-- end sign -->")
    for action, label in (("shoot:dunk", "DUNK"), ("shoot:three", "3-POINTER"), ("close", "LEAVE IT")):
        assert f'data-action="{action}"' in sign and label in sign, action


@pytest.mark.parametrize("shot, who, flash, figure", [
    ("dunk", "needle", "SLAM!", "<!-- Fantastic Needle"),
    ("three", "bible", "SWISH!", "<!-- MC Bible (black leather jacket, shooting)"),
    ("three", "needle", "SWISH!", "<!-- Fantastic Needle"),  # when Bible carries his book
])
def test_each_shot_plays_once_when_picked(shot, who, flash, figure):
    svg = BLOCK.read_text()
    play = part(svg, f'id="shot-{shot}-{who}"', f"<!-- end shot-{shot}-{who} -->")
    assert figure in play and flash in play
    assert 'begin="indefinite"' in play  # it starts when the player picks it, and plays once
    overlay = svg[svg.rindex("<g", 0, svg.index(f'<g id="shot-{shot}-{who}"')):][:200]
    assert f'data-overlay="shot-{shot}-{who}"' in overlay
    assert 'data-auto-action="shot_done"' in overlay  # when it's over, back to normal


def test_for_the_dunk_bible_lobs_it_from_the_line_and_needle_catches_it_in_the_air():
    # changed: Bible passes instead of Meyhem. He walks to the ball, goes back to the three-point
    # line and lobs it up; Needle has to jump, catch it in the air and dunk it, then he hangs on
    # the rim for 1-2 seconds, drops down and goes back
    svg = BLOCK.read_text()
    play = part(svg, 'id="shot-dunk-needle"', "<!-- end shot-dunk-needle -->")
    assert "<!-- MC Meyhem" not in play
    for book in ("lacks", "has"):  # with his hands free, or the rhyme book in the other hand
        bible = part(play, f'data-overlay="{book}-rhyme_book"', "<!-- end dunk-bible -->")
        assert bible.count("<!-- MC Bible (black leather jacket") == 3, book  # over to the ball, back to the line, the pass
    assert 'id="dunkGo"' in play and "dunkGo.begin" in play
    timing = lambda g: re.search(r'values="([^"]+)" keyTimes="([^"]+)" dur="([\d.]+)s"', g)
    def keys(g):
        m = timing(g)
        return ([tuple(map(float, v.split())) for v in m.group(1).split(";")],
                [float(t) * float(m.group(3)) for t in m.group(2).split(";")])
    needle_moves, needle_t = keys(part(play, 'id="dunk-needle"', "</g>"))
    ball_moves, ball_t = keys(part(play, 'id="dunk-ball"', "</g>"))
    release = next(x for (x, y), t in zip(ball_moves, ball_t) if y < 300 and x > 500)  # thrown from behind the arc
    assert release > 500
    catch_t = next(t for (x, y), t in zip(ball_moves, ball_t) if abs(x - 300) < 6 and y < 205)  # the ball at the rim ...
    up = [t for t, (_, dy) in zip(needle_t, needle_moves) if dy <= -40]
    assert up[0] <= catch_t <= up[0] + 0.1                                             # ... as Needle gets up there
    assert 1.0 <= up[-1] - up[0] <= 2.0                                                # hanging on the rim
    assert needle_moves[-1] == (0.0, 0.0)
    assert 'data-overlay="!meyhem-shooting"' not in svg


def test_the_shooter_isnt_in_his_spot_meanwhile():
    svg = BLOCK.read_text()
    assert 'data-overlay="!needle-shooting"' in svg
    assert 'data-overlay="lacks-rhyme_book !bible-shooting"' in svg
    # changed: Bible's spot also empties while he passes for the dunk (with or without his book)
    assert re.search(r'data-overlay="has-rhyme_book !bible-shooting"[^>]*>\s*<!-- MC Bible \(black leather jacket, rhyme book\)', svg)


def on_the_block(db_file, inventory=()):
    save_game(db_file, GameState(current_scene="block", inventory=list(inventory)))
    at = start_app()
    choose(at, "resume")
    return at


def test_picking_a_shot_in_the_app(db_file):
    at = on_the_block(db_file)
    saved = load_game(db_file)
    choose(at, "inspect:basketball", screen="picture")
    assert "inspect-basketball" in picture(at)["show"]
    assert {"shoot:dunk", "shoot:three", "close"} <= set(picture(at)["enabled"])
    choose(at, "shoot:dunk", screen="picture")
    shown = picture(at)
    assert {"shooting", "shot-dunk-needle", "needle-shooting", "bible-shooting"} <= set(shown["show"])  # changed: Bible passes
    assert "inspect-basketball" not in shown["show"]
    choose(at, "shot_done", screen="picture")
    assert "shooting" not in picture(at)["show"]
    assert load_game(db_file) == saved  # just for fun: nothing changes, nothing is saved


@pytest.mark.parametrize("inventory, who", [((), "bible"), (("rhyme_book",), "needle")])
def test_who_takes_the_three(db_file, inventory, who):
    at = on_the_block(db_file, inventory)
    choose(at, "inspect:basketball", screen="picture")
    choose(at, "shoot:three", screen="picture")
    assert {f"shot-three-{who}", f"{who}-shooting"} <= set(picture(at)["show"])


def test_ways_out_and_the_key_hint():
    svg = BLOCK.read_text()
    # changed: 149 ST STATION walks the crew to the station gate (the gate is its own place now)
    assert 'data-action="enter_station"' not in svg and svg.count('data-action="go_gate"') == 1
    # changed: the ways out are street signs now (specs/point-and-click.md): GOODFELLAS HQ for the basement
    assert 'data-action="go_hq"' in svg and "GOODFELLAS HQ" in svg
    assert 'data-action="go_record_shop"' in svg and "RICO&#39;S RECORDS" in svg  # the block leads everywhere
    assert 'data-overlay="has-service_key"' in svg  # a glinting key once the crew has it


def test_the_whole_crew_is_there_and_portals_studies_the_tags():
    svg = BLOCK.read_text()
    for member in ("Fantastic Needle", "MC Bible", "MC Meyhem", "Reekz"):
        assert f"<!-- {member}" in svg
    assert "<!-- Portals (from behind" in svg


def test_block_conversation():
    dialogue = SCENES["block"]["dialogue"]
    lines = " ".join(line for _, line in dialogue)
    assert "TAGS" in lines and "STATION" in lines and "KEY" in lines
    svg = BLOCK.read_text()
    for i in range(len(dialogue)):
        assert f'data-overlay="talk-{i}"' in svg


def test_arriving_on_the_block(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    shown = picture(at)
    assert shows_picture(at, "scene-block")
    assert len(at.main.header) == 0 and len(at.main.markdown) == 0 and len(at.main.button) == 0
    assert shown["show"][0] == "talk-0"
    assert {"go_gate", "go_hq", "go_record_shop", "go_battle", "next"} <= set(shown["enabled"])  # changed: go_gate
    assert "has-service_key" not in shown["show"]


# changed: the gate stays shut without the key (A1) and opens with it (A2) at the station gate
# now, see test_walk_to_station.py


def test_back_to_the_basement(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    act(at, "go_hq")
    assert shows_picture(at, "scene-hq")


def test_rejected_message_is_the_one_from_the_rules():
    # changed: the gate (and its message) is at the station gate now, not on the block
    gate = (ROOT / "assets" / "scenes" / "gate.svg").read_text()
    sign = part(gate, 'data-overlay="rejected-enter_station"', "<!-- end rejected -->")
    assert LOCKED_STATION_MESSAGE.upper() in sign
    assert 'data-overlay="rejected-enter_station"' not in BLOCK.read_text()


def test_block_asset_matches_its_source():
    assert BLOCK.read_text() == build.block_scene()


# --- the ball goes through the hoop: the front of the rim and the net are in front of it ---

SHOTS = ("shot-dunk-needle", "shot-three-bible", "shot-three-needle")


@pytest.mark.parametrize("shot", SHOTS)
def test_the_ball_drops_through_the_rim_and_net(shot):
    play = part(BLOCK.read_text(), f'id="{shot}"', f"<!-- end {shot} -->")
    ball = play[play.index('<circle r="11" fill="#e8742a"'):]
    assert 'class="hoop-front"' in ball                      # rim front and net drawn after (over) the ball
    assert "swish" in ball[ball.index('class="hoop-front"'):]   # the net stretches as it goes through
    path = re.search(r'<g(?: id="[^"]+")?><animateTransform attributeName="transform" type="translate" values="([^"]+)"',
                     play[play.rindex("<g", 0, play.index('<circle r="11" fill="#e8742a"')):]).group(1)
    points = [tuple(map(float, p.split())) for p in path.split(";")]
    above = next(i for i, (x, y) in enumerate(points) if abs(x - 300) < 6 and y < 215)
    assert any(abs(x - 300) < 6 and y > 255 for x, y in points[above:])  # straight down through the net


def test_the_hoop_front_is_in_front_of_the_court_when_nobody_shoots():
    svg = BLOCK.read_text()
    front = svg.index('<g data-overlay="!shooting"><g class="hoop-front"')
    assert front > svg.index('id="shot-three-needle"')       # on top of everything on the court


def test_needle_dunks_in_front_of_the_hoop():
    # he is in front of the rim and the net (the ball goes through behind the rim's front)
    play = part(BLOCK.read_text(), 'id="shot-dunk-needle"', "<!-- end shot-dunk-needle -->")
    assert play.index('class="hoop-front"') < play.index('id="dunk-needle"')
    assert play.index('id="dunk-ball"') < play.index('class="hoop-front"')
