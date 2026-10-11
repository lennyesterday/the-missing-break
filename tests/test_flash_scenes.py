"""The Grandmaster Flash layer in the app and its pictures: the first try in the basement,
Portals' portal, Flash's realm, the corner store, the cypher's prize, the crayon marks."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import CRAYON_MESSAGE, NO_MONEY_MESSAGE, GameState
from tests.apphelpers import act, choose, picture, shows_picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
HQ = (ROOT / "assets" / "scenes" / "hq.svg").read_text()
BLOCK = (ROOT / "assets" / "scenes" / "block.svg").read_text()
FLASH = ROOT / "assets" / "scenes" / "flash.svg"
STORE = ROOT / "assets" / "scenes" / "corner_store.svg"
WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def at(db_file, **state):
    save_game(db_file, GameState(**state))
    app = start_app()
    choose(app, "resume")
    return app


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


# --- the basement: Needle can't catch the break, Portals opens the portal ---

def test_needle_tries_and_cant(db_file):
    app = at(db_file, current_scene="hq", inventory=WITH_RECORD)
    act(app, "try_practice")
    assert "done-try_practice" in picture(app)["show"] and "stuck" in picture(app)["show"]
    assert load_game(db_file).stuck is True
    assert "go_flash" in picture(app)["enabled"]


def test_the_basement_buttons():
    assert 'data-overlay="stuck"' in HQ[HQ.rindex("<g", 0, HQ.index('data-action="go_flash"')) - 60:HQ.index('data-action="go_flash"')]
    assert "PORTAL TO FLASH" in HQ
    for sign in ("done-try_practice", "rejected-practice"):
        assert f'data-overlay="{sign}"' in HQ, sign
    assert CRAYON_MESSAGE.upper()[:30] in HQ


def test_without_crayons_flash_reminds_him(db_file):
    app = at(db_file, current_scene="hq", inventory=WITH_RECORD, stuck=True, met_flash=True)
    choose(app, "practice", screen="picture")
    assert "rejected-practice" in picture(app)["show"]
    assert svg_screen(app, "crayon") is None


# --- through the portal, to Grandmaster Flash and back ---

@pytest.mark.parametrize("scene, action, walk, arrives", [
    ("hq", "go_flash", "assets/walks/hq__flash.svg", "scene-flash"),
    ("flash", "go_hq", "assets/walks/flash__hq.svg", "scene-hq"),
])
def test_through_portals_portal(db_file, scene, action, walk, arrives):
    app = at(db_file, current_scene=scene, inventory=WITH_RECORD, stuck=True, met_flash=scene == "flash")
    choose(app, action, screen="picture")
    assert app.session_state["walk"] == walk
    assert re.search(r'<svg[^>]*data-auto-action="enter"', picture(app)["svg"])  # it goes on by itself
    choose(app, "enter", screen="picture")
    assert shows_picture(app, arrives)


def test_portals_sprays_the_portal_in_his_corner():
    svg = (ROOT / "assets" / "walks" / "hq__flash.svg").read_text()
    assert "<!-- Portals (denim" in svg and 'id="flash-portal"' in svg and 'class="tunnel"' in svg
    assert 'id="graffiti-corner"' in svg                        # in the basement
    assert re.search(r'id="camera"', svg)                       # and the camera goes through it
    back = (ROOT / "assets" / "walks" / "flash__hq.svg").read_text()
    assert 'id="flash-realm"' in back and 'class="tunnel"' in back


def test_flash_the_guru():
    svg = FLASH.read_text()
    assert 'id="scene-flash"' in svg and 'id="flash-realm"' in svg
    assert "<!-- Grandmaster Flash" in svg
    for p in ('id="halo"', 'id="floating-records"', 'id="spinning-floor"', 'id="flash-decks"'):
        assert p in svg, p
    assert 'data-action="go_hq"' in svg and "THROUGH THE PORTAL" in svg
    assert svg.count('data-overlay="talk-') >= 7


def test_meeting_flash_is_saved(db_file):
    app = at(db_file, current_scene="hq", inventory=WITH_RECORD, stuck=True)
    act(app, "go_flash")
    assert load_game(db_file).met_flash is True and load_game(db_file).current_scene == "flash"


# --- the corner store ---

def test_into_the_corner_store_any_time(db_file):
    app = at(db_file, current_scene="block")
    assert "go_store" in picture(app)["enabled"]
    act(app, "go_store")
    assert shows_picture(app, "scene-corner-store")
    act(app, "buy_crayons")
    assert "rejected-buy_crayons" in picture(app)["show"]
    sign = part(picture(app)["svg"], 'data-overlay="rejected-buy_crayons"', "<!-- end rejected -->")
    assert NO_MONEY_MESSAGE.upper()[:30] in sign
    assert load_game(db_file).money == 0


def test_buying_crayons_in_the_app(db_file):
    app = at(db_file, current_scene="corner_store", money=1000, met_flash=True)
    act(app, "buy_crayons")
    assert load_game(db_file).inventory == ["crayons"] and load_game(db_file).money == 900
    assert "offer-buy_crayons" not in picture(app)["show"]       # gone from the shelf
    assert "$9.00" in "".join(str(e.value) for e in app.sidebar.markdown)  # the money, in the sidebar


def test_the_corner_store_picture():
    svg = STORE.read_text()
    for item, price in (("crayons", "$1.00"), ("chips", "50¢"), ("soda", "25¢"), ("candy", "10¢")):
        shelf = part(svg, f'data-overlay="offer-buy_{item}"', "</g></g>")
        assert f'data-action="buy_{item}"' in shelf and price in shelf, item
    assert "<!-- Store clerk" in svg and 'data-action="go_block"' in svg
    assert 'data-action="go_store"' in BLOCK                     # the store's door on the block


# --- the cypher: only after Flash, and the prize ---

def test_the_cypher_shows_up_after_flash():
    overlay = BLOCK[BLOCK.rindex("<g", 0, BLOCK.index('id="cypher"')) - 80:BLOCK.index('id="cypher"')]
    assert 'data-overlay="met-flash"' in overlay


def test_no_cypher_before_flash(db_file):
    app = at(db_file, current_scene="block")
    assert "inspect:cypher" not in picture(app)["enabled"] and "met-flash" not in picture(app)["show"]
    assert "win_cypher" not in picture(app)["enabled"]           # never a button


def test_winning_the_cypher_pays_in_the_app(db_file):
    from tests.test_cypher_battle import play_set
    app = at(db_file, current_scene="block", met_flash=True)
    choose(app, "inspect:cypher", screen="picture")
    choose(app, "join:cypher", screen="picture")
    choose(app, "reekz_turn", screen="cypher")
    play_set(app, ["toprock", "helicopter", "headspin", "freeze"])
    choose(app, "next_round", screen="cypher")
    choose(app, "reekz_turn", screen="cypher")
    play_set(app, ["helicopter", "nineteen_ninety", "freeze"])
    assert "cypher-won" in svg_screen(app, "cypher")["show"]
    assert load_game(db_file).money == 1000                     # $10 for the crew, saved
    choose(app, "leave_cypher", screen="cypher")
    assert "done-win_cypher" in picture(app)["show"]


# --- the crayon: marking the break, then keeping it going ---

def test_with_crayons_needle_marks_the_break_first(db_file):
    app = at(db_file, current_scene="hq", inventory=WITH_RECORD + ["crayons"], stuck=True, met_flash=True)
    choose(app, "practice", screen="picture")
    choose(app, "decks_ready", screen="picture")
    crayon = svg_screen(app, "crayon")
    assert crayon is not None and crayon["file"] == "assets/screens/crayon.svg"
    assert "marks-0" in crayon["show"] and {"mark_hit", "mark_miss", "stop_practice"} <= set(crayon["enabled"])
    choose(app, "mark_miss", screen="crayon")                    # not when the loop starts over: no mark
    assert "marks-0" in svg_screen(app, "crayon")["show"] and "not-there" in svg_screen(app, "crayon")["show"]
    # changed: two marks (it was three), one on each copy. When the break is over and he MARKs, his
    # hand stops the record (the beat stops), draws the mark and lets it go (the beat goes on)
    for n in (1, 2):
        choose(app, "mark_hit", screen="crayon")
        shown = svg_screen(app, "crayon")
        assert {f"marks-{n}", "marking"} <= set(shown["show"])
        assert shown["enabled"] == ["mark_done", "stop_practice"]          # nothing to press meanwhile
        assert shown["audio"]["cmd"] == "pause"                             # the record is stopped
        choose(app, "mark_done", screen="crayon")
        if n == 1:
            shown = svg_screen(app, "crayon")
            assert "marking" not in shown["show"] and shown["audio"]["cmd"] == "resume"  # let go: the beat goes on
    assert svg_screen(app, "crayon") is None and svg_screen(app, "practice") is not None  # two marks: keep it going
    assert svg_screen(app, "practice")["audio"]["cmd"] == "resume"
    assert load_game(db_file).practiced is False


def test_the_crayon_screen():
    svg = (ROOT / "assets" / "screens" / "crayon.svg").read_text()
    tag = svg[:svg.index(">")]
    assert 'data-sync="audio"' in tag and 'data-auto-action="mark_miss"' in tag
    for n in range(3):  # changed: two marks
        assert re.search(rf'data-overlay="marks-{n}[" ]', svg), n
    assert 'data-pause-on="mark_hit"' in tag                    # the beat stops right as he presses
    for k in (1, 2):                                            # both turntables; his hand marks each in turn
        marking = svg[svg.index(f'id="marking-{k}"'):svg.index(f"<!-- end marking-{k} -->")]
        assert 'data-auto-action="mark_done"' in svg[svg.rindex("<g", 0, svg.index(f'id="marking-{k}"')):svg.index(f'id="marking-{k}"')]
        assert 'id="needle-hand"' in marking and 'class="crayon"' in marking
        assert 'attributeName="stroke-dashoffset"' in marking        # the mark is drawn
        assert 'begin="indefinite"' in marking                       # when he presses, not when the page loads
    assert svg.count('class="deck"') >= 4
    assert "dataset.pauseOn" in (ROOT / "app.py").read_text()          # the page stops the music then and there
    assert "MARK" in svg and 'data-defer="1"' in svg and "THE SECRET LIES IN THE CRAYON" in svg
    assert 'class="crayon-mark"' in (ROOT / "assets" / "screens" / "practice.svg").read_text()  # marks on the decks


@pytest.mark.parametrize("asset, make", [
    ("assets/scenes/flash.svg", build.flash_scene), ("assets/scenes/corner_store.svg", build.corner_store_scene),
    ("assets/walks/hq__flash.svg", build.walk_hq_to_flash), ("assets/walks/flash__hq.svg", build.walk_flash_to_hq),
    ("assets/screens/crayon.svg", build.crayon_screen),
])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()
