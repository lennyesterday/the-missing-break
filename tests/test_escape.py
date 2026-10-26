"""The escape: between the story intro and the basement. Portals, chased by the police, sprays a
portal on a wall, it opens onto the basement and he jumps through. The camera follows him in."""

import json
import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import INTRO_MUSIC, SONGS, GameState
from tests.apphelpers import choose, intro_screen, picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
ESCAPE = (ROOT / "assets" / "screens" / "escape.svg").read_text()
END = float(re.search(r'data-end="([\d.]+)"', ESCAPE).group(1))
CUES = {c["src"].split("/")[-1]: c for c in json.loads(re.search(r"data-cues='([^']*)'", ESCAPE).group(1))}


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(start, end):
    piece = ESCAPE[ESCAPE.index(start):]
    return piece[:piece.index(end)]


def escape_screen(at):
    return svg_screen(at, "escape")


# --- in the app ---

def test_lets_go_leads_to_the_escape(db_file):
    at = start_app()
    choose(at, "start")
    choose(at, "go", screen="intro")
    assert intro_screen(at) is None
    assert escape_screen(at) is not None
    assert escape_screen(at)["enabled"] == ["arrive"]
    assert picture(at) is None                     # the basement comes after it
    # changed: the intro song fades out as soon as LET'S GO is pressed (it used to play on through the escape)
    assert escape_screen(at)["ambience"] is None
    assert load_game(db_file) == GameState(current_scene="hq", inventory=[])  # nothing changes


def test_when_it_is_over_the_game_starts_in_the_basement(db_file):
    at = start_app()
    choose(at, "start")
    choose(at, "go", screen="intro")
    choose(at, "arrive", screen="escape")          # automatically at the end, or SKIP
    assert escape_screen(at) is None
    assert at.session_state["game"].current_scene == "hq"
    assert picture(at) is not None and "go_block" in picture(at)["enabled"]


def test_resume_skips_the_escape(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=[]))
    at = start_app()
    choose(at, "resume")
    assert escape_screen(at) is None and intro_screen(at) is None


# --- the picture ---

def test_it_goes_on_by_itself_and_can_be_skipped():
    assert re.search(r'<svg[^>]*data-auto-action="arrive"', ESCAPE)
    assert float(re.search(r'data-auto-delay="([\d.]+)"', ESCAPE).group(1)) == END
    skip = part('aria-label="Skip to the basement"', "</g>")
    assert "SKIP" in skip
    assert 'data-action="arrive"' in ESCAPE[ESCAPE.rindex("<g", 0, ESCAPE.index('aria-label="Skip to the basement"')):]
    assert END >= 9  # changed: longer, with the landing in the basement


def test_portals_runs_in_and_sprays_the_portal_on_the_ground():
    # changed: the portal is sprayed on the ground (it used to be on the wall)
    assert 'id="escape-screen"' in ESCAPE
    assert "<!-- Portals (denim" in ESCAPE                  # running in
    assert "<!-- Portals (from behind, painting) -->" in ESCAPE  # spraying the ring
    ring = part('id="portal-ring"', "<!-- end portal-ring -->")
    assert "stroke-dashoffset" in ring                       # the ring is sprayed bit by bit
    cy = float(re.search(r'<ellipse cx="[\d.]+" cy="([\d.]+)"', ring).group(1))
    assert cy > 385                                          # on the ground of the alley


def test_he_says_his_line_while_he_makes_it():
    voice = CUES["portals_says.mp3"]
    assert (ROOT / "static" / "audio" / "escape" / "portals_says.mp3").is_file()
    assert "escape/portals_says.mp3" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()
    bubble = part('id="portals-says"', "<!-- end portals-says -->")
    assert "THEY CALL ME PORTALS FOR A REASON." in bubble
    (a, b), = voice["on"]
    spray_from, spray_to = CUES["spray.mp3"]["on"][0]
    assert spray_from <= a < spray_to                        # while he sprays the portal
    assert re.search(rf'to="visible" begin="{a:.2f}s"', bubble)
    # nobody shouts over him, and he is the loudest thing in the scene
    for name in ("police_shout.mp3", "police_dog.mp3"):
        for c, d in CUES[name]["on"]:
            assert d <= a or c >= b, name
    assert all(cue["vol"] < voice["vol"] for name, cue in CUES.items() if name != "portals_says.mp3")


def test_the_portal_looks_like_a_portal():
    # changed: a glowing, swirling tunnel with sparks, a beam of light and rising sparkles
    portal = part('id="portal"', "<!-- end portal -->")
    assert 'type="rotate"' in portal                          # the swirl
    assert portal.count('class="tunnel"') >= 3                # rings falling away into the depth
    assert 'class="sparks"' in portal and "stroke-dashoffset" in portal  # crackling along the rim
    assert 'class="beam"' in portal and 'class="sparkle"' in portal


def test_portals_jumps_straight_in():
    jump = part('id="portals-jumps"', "<!-- end portals-jumps -->")
    assert "<!-- Portals (denim" in jump and 'type="scale"' in jump


def test_and_lands_in_the_basement():
    landing = part('id="basement-landing"', "<!-- end basement-landing -->")
    assert 'id="ceiling-portal"' in landing                         # he drops out of the ceiling
    fall = part('id="portals-lands"', "<!-- end portals-lands -->")
    assert "<!-- Portals (denim" in fall
    # where he stands in the basement scene, so the game picks up right there
    assert re.search(r'values="700 -?[\d.]+;700 327"', fall)
    assert "crew.portals(700" in (ROOT / "art" / "build.py").read_text()


def test_the_basement_he_lands_in_is_the_basement_scene():
    # changed: it used to be a simpler, emptier basement, so the room changed when the game began
    landing = part('id="basement-landing"', "<!-- end basement-landing -->")
    hq = (ROOT / "assets" / "scenes" / "hq.svg").read_text()
    for thing in ("graffiti-corner", "sopranos-crossout", "checkerboard-floor", "vinyls", "soundsystem", "couch",
                  "rhyme-book", "turntables", "empty-crate", "empty-sleeve", "comic-posters"):
        assert f'id="{thing}"' in hq and f'id="{thing}"' in landing, thing
    for who in ("Fantastic Needle", "MC Bible (black leather jacket, pointing)", "Reekz (breaking"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert f"<!-- {who}" in landing, who
    # the same records, in the same places
    assert re.findall(r'<title>([^<]*)</title>', part('id="vinyls"', "<!-- end vinyls -->")) == \
        re.findall(r'<title>([^<]*)</title>', hq[hq.index('id="vinyls"'):hq.index("<!-- end vinyls -->")])
    # just a picture: nothing to click, nothing the page has to show or hide
    assert "data-action" not in landing and "data-overlay" not in landing
    # and when he has landed he goes back to spraying his corner, as in the basement scene
    assert "<!-- Portals (denim" in part('id="portals-back-in-his-corner"', "<!-- end portals-back-in-his-corner -->")


def test_a_nicer_alley():
    for p in ('id="night-sky"', 'id="fire-escape"', 'id="police-car"', 'id="manhole"', 'id="puddles"', 'id="dumpster"',
              'id="posters"'):
        assert p in ESCAPE, p


def test_the_police_come_too_late():
    chase = part('id="escape-police"', "<!-- end escape-police -->")
    assert chase.count("<!-- Police officer") >= 2 and "<!-- Police dog" in chase
    assert "STOP! POLICE!" in chase and "WHERE&#39;D HE GO?!" in chase.replace("'", "&#39;")


def test_the_camera_follows_him_into_the_portal():
    camera = part('id="camera"', "<!-- end camera -->")
    assert 'type="scale"' in camera and 'type="translate"' in camera


def test_the_sounds_of_the_chase_and_the_spray():
    assert set(CUES) == {"spray.mp3", "siren.mp3", "police_shout.mp3", "police_dog.mp3", "portals_says.mp3"}
    music = SONGS[INTRO_MUSIC]["volume"]
    for name, cue in CUES.items():
        if name != "portals_says.mp3":
            assert 0 < cue["vol"] < music, name  # the effects stay as quiet as in the intro
        for a, b in cue["on"]:
            assert 0 <= a < b <= END, name


def test_asset_matches_its_source():
    assert ESCAPE == build.escape_screen()


def test_the_page_goes_on_by_itself_on_the_pictures_clock():
    app = (ROOT / "app.py").read_text()
    assert "dataset.autoAction" in app and "getCurrentTime" in app
