"""Through the doors (specs/additional-scenes.md): the crew comes out of the door of the place it
leaves, one after the other, and goes in through the door of the place it gets to. Clicking Rico's
door or the open station gate plays them going in before the place comes up. New walks to the
corner store (and back) and to Disco Fever."""

import re
from pathlib import Path

import pytest

from art import build
from db import save_game
from logic import GameState
from tests.apphelpers import choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
WALKS = ROOT / "assets" / "walks"
APP = (ROOT / "app.py").read_text()
CREW = ("Reekz", "Fantastic Needle", "Portals (denim", "MC Bible")


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def walk(name):
    return (WALKS / f"{name}.svg").read_text()


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def crew_in(piece):
    return all(f"<!-- {who}" in piece for who in CREW)


# --- coming out, going in ---

@pytest.mark.parametrize("name, door", [("hq__block", "hq-door"), ("block__hq", "court-gate"),
                                        ("record_shop__block", "ricos-door"), ("station__block", "station-arch"),
                                        ("corner_store__block", "store-door")])
def test_the_crew_comes_out_of_the_door_one_after_the_other(name, door):
    svg = walk(name)
    out = part(svg, f'id="crew-out-of-{door}"', f"<!-- end crew-out-of-{door} -->")
    assert crew_in(out), name
    # each one shows up at the door later than the one before
    starts = [float(t) for t in re.findall(r'<set attributeName="visibility" to="visible" begin="([\d.]+)s"', out)]
    assert len(starts) == 4 and len(set(starts)) == 4, starts
    assert f'id="{door}-open"' in svg  # the door stands open while they come out


@pytest.mark.parametrize("name, door", [("hq__block", "court-gate"), ("block__hq", "hq-door"),
                                        ("block__corner_store", "store-door"), ("block__battle", "club-door")])
def test_at_the_end_the_crew_goes_in_through_the_door_by_itself(name, door):
    svg = walk(name)
    into = part(svg, f'id="crew-into-{door}"', f"<!-- end crew-into-{door} -->")
    assert crew_in(into), name
    gone = [float(t) for t in re.findall(r'<animate attributeName="opacity" values="1;0" begin="([\d.]+)s"', into)]
    assert len(gone) == 4 and len(set(gone)) == 4, gone  # one after the other
    assert f'id="{door}-open"' in svg
    auto = float(re.search(r'<svg[^>]*data-auto-delay="([\d.]+)"', svg).group(1))
    assert auto >= max(gone)  # the next place comes up once the last one is in


@pytest.mark.parametrize("name, door, label", [("block__record_shop", "ricos-door", "ENTER RICO"),
                                               ("gate__station", "station-arch", "ENTER THE STATION")])
def test_clicking_the_door_plays_them_going_in(name, door, label):
    svg = walk(name)
    assert "data-auto-action" not in svg[:300]  # it still waits at the door
    found = re.search(r'<g [^>]*data-plays="goIn"[^>]*>', svg)
    assert found and label in svg[found.start():svg.index("<!-- end exit -->", found.start())]
    button = found.group(0)
    assert 'data-action="enter"' in button
    delay = float(re.search(r'data-action-delay="([\d.]+)"', button).group(1))
    assert re.search(r'<animate id="goIn" [^>]*begin="indefinite"', svg)
    into = part(svg, f'id="crew-into-{door}"', f"<!-- end crew-into-{door} -->")
    assert crew_in(into)
    assert 'begin="goIn.begin"' in into  # they only start once the door is clicked
    gone = [float(t) for t in re.findall(r'values="1;0" begin="goIn.begin\+([\d.]+)s"', into)]
    assert len(gone) == 4 and delay >= max(gone)
    waiting = part(svg, 'id="crew-waiting"', "<!-- end crew-waiting -->")
    assert '<set attributeName="visibility" to="hidden" begin="goIn.begin"' in waiting
    assert f'id="{door}-open"' in svg


def test_down_the_stairs_into_the_station():
    into = part(walk("gate__station"), 'id="crew-into-station-arch"', "<!-- end crew-into-station-arch -->")
    down = f'type="translate" values="0 0;0 {build.STAIRS_DROP}"'
    assert into.count(down) == 4  # each one goes down as he goes in


def test_up_the_stairs_out_of_the_station():
    out = part(walk("station__block"), 'id="crew-out-of-station-arch"', "<!-- end crew-out-of-station-arch -->")
    up = f'type="translate" values="0 {build.STAIRS_DROP};0 0"'
    assert out.count(up) == 4  # each one comes up as he comes out


def test_the_page_plays_a_door_before_going_on():
    assert "dataset.plays" in APP and "dataset.actionDelay" in APP


# --- out of the station with the record ---

def test_needle_holds_the_record_up_when_they_won_it():
    svg = walk("station__block")
    won = part(svg, 'data-overlay="has-vinyl"', "<!-- end has-vinyl -->")
    assert "WE GOT IT BACK!" in won and 'id="record-held-up"' in won
    assert "OUT OF THE STATION" in part(svg, 'data-overlay="lacks-vinyl"', "<!-- end lacks-vinyl -->")


def test_coming_out_of_the_station_with_the_record_in_the_app(db_file):
    save_game(db_file, GameState(current_scene="station", inventory=["rhyme_book", "service_key", "vinyl"], rap_battle="won"))
    at = start_app()
    choose(at, "resume")
    choose(at, "go_block", screen="picture")
    assert at.session_state["walk"] == "assets/walks/station__block.svg"
    assert "has-vinyl" in picture(at)["show"]


# --- the new walks ---

def test_the_corner_store_walks():
    there, back = walk("block__corner_store"), walk("corner_store__block")
    for svg in (there, back):
        assert 'id="corner-store"' in svg and 'id="court-wall"' in svg
    assert 'id="crew-walking-back" transform="translate(800 0) scale(-1 1)"' in back


def test_disco_fever_from_outside():
    svg = walk("block__battle")
    club = part(svg, 'id="club-front"', "<!-- end club-front -->")
    # changed: Disco Fever is called the Borough DJ Battle now (product owner, specs/additional-little-conversations-and-scenes.md)
    assert "Borough DJ Battle" in club and "BOROUGH FINAL" in club
    assert 'id="velvet-rope"' in svg and 'id="bouncer"' in svg
    assert svg.count('class="onlooker"') >= 5  # the line of people waiting
    assert "GOODFELLAS! GO ON IN." in svg
    rope = part(svg, 'id="velvet-rope"', "<!-- end velvet-rope -->")
    assert 'attributeName="d"' in rope  # the bouncer unhooks it for the crew: it drops


@pytest.mark.parametrize("scene, action, name", [("block", "go_store", "block__corner_store"),
                                                 ("corner_store", "go_block", "corner_store__block"),
                                                 ("block", "go_battle", "block__battle")])
def test_the_new_walks_in_the_app(db_file, scene, action, name):
    save_game(db_file, GameState(current_scene=scene, inventory=[]))
    at = start_app()
    choose(at, "resume")
    choose(at, action, screen="picture")
    assert at.session_state["walk"] == f"assets/walks/{name}.svg"
    choose(at, "enter", screen="picture")  # by itself at the end, or SKIP
    assert not at.session_state["walk"]


@pytest.mark.parametrize("asset, make", [
    ("assets/walks/hq__block.svg", build.walk_hq_to_block),
    ("assets/walks/block__hq.svg", build.walk_block_to_hq),
    ("assets/walks/block__record_shop.svg", build.walk_block_to_record_shop),
    ("assets/walks/record_shop__block.svg", build.walk_record_shop_to_block),
    ("assets/walks/gate__station.svg", build.walk_gate_to_station),
    ("assets/walks/station__block.svg", build.walk_station_to_block),
    ("assets/walks/block__corner_store.svg", build.walk_block_to_corner_store),
    ("assets/walks/corner_store__block.svg", build.walk_corner_store_to_block),
    ("assets/walks/block__battle.svg", build.walk_block_to_battle),
])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()
