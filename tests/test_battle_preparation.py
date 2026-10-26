"""Battle preparation (specs/battle-preparation.md): back on the block from the station with the
record won back, the crew celebrates Bible and Needle says they still have to practice. Then, in
the basement, Needle tries the break at his turntables and can't loop it, the crew decides to find
Grandmaster Flash, and Portals' spray cans open the portal."""

import re
import wave
from pathlib import Path

import pytest

from db import load_game, save_game
from logic import SCENES, SONGS, GameState, apply_action, conversation
from tests.apphelpers import act, choose, picture, shows_picture, start_app

ROOT = Path(__file__).parent.parent
BLOCK = (ROOT / "assets" / "scenes" / "block.svg").read_text()
LINES = [
    ("reekz", "BIBLE, YOU KILLED THAT ONE!"),
    ("bible", "THEY CALL ME BIBLE 'CAUSE I NEVER RUN OUT OF VERSES."),
    ("needle", "NOW THAT WE GOT MY RECORD BACK, WE'RE READY FOR THE DJ BATTLE. WE JUST NEED TO PRACTICE."),
]
WON = GameState(current_scene="block", inventory=["rhyme_book", "service_key", "vinyl"], rap_battle="won",
                left_scenes=["hq", "block", "record_shop", "gate", "station"])


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def bubbles(at):
    return [s for s in picture(at)["show"] if s.startswith(("talk-", "back-", "after-", "won-", "stuck-"))]


# --- the rules ---

def test_the_lines():
    assert SCENES["block"]["dialogue_won"]["lines"] == LINES


def test_from_the_station_with_the_record():
    assert conversation(WON, came_from="station") == ("won", LINES)


def test_not_from_anywhere_else():
    assert conversation(WON, came_from="hq")[0] != "won"
    assert conversation(WON)[0] != "won"  # e.g. after a restart


def test_not_without_the_record():
    lost_nothing = GameState(current_scene="block", inventory=["service_key"], left_scenes=["block", "station"])
    assert conversation(lost_nothing, came_from="station")[0] != "won"


# --- in the app ---

def test_back_on_the_block_after_the_win(db_file):
    save_game(db_file, GameState(current_scene="station", inventory=["rhyme_book", "service_key", "vinyl"],
                                 rap_battle="won", left_scenes=["hq", "block", "record_shop", "gate"]))
    at = start_app()
    choose(at, "resume")
    act(at, "go_block")  # the walk out of the station, then the block
    for i in range(len(LINES)):
        assert bubbles(at) == [f"won-{i}"]
        choose(at, "next", screen="picture")
    assert bubbles(at) == []
    saved = load_game(db_file)
    assert saved.current_scene == "block" and "vinyl" in saved.inventory  # talking changes nothing
    # ... and not again coming back from somewhere else
    act(at, "go_hq")
    act(at, "go_block")
    assert bubbles(at) == []


def test_after_a_restart_no_bubble(db_file):
    save_game(db_file, WON)
    at = start_app()
    choose(at, "resume")
    assert bubbles(at) == []


# --- the picture ---

def test_the_bubbles_are_in_the_block_picture():
    for i, (speaker, line) in enumerate(LINES):
        bubble = BLOCK[BLOCK.index(f'data-overlay="won-{i}"'):]
        bubble = bubble[:bubble.index("</g>")]
        assert line.split()[0].replace("'", "&#39;") in bubble, i


# === part 2: Needle tries the break, Portals sprays the portal ===

HQ = (ROOT / "assets" / "scenes" / "hq.svg").read_text()
TO_FLASH = (ROOT / "assets" / "walks" / "hq__flash.svg").read_text()
WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]
STUCK_LINES = [
    ("bible", "THAT TAKES TOO LONG. WE'LL NEVER MAKE IT IN TIME FOR THE BATTLE!"),
    ("needle", "THERE'S ONLY ONE MAN WHO CAN HELP US LOOP THE BREAK."),
    ("reekz", "AND WHO'S THAT?"),
    ("needle", "THE GRANDMASTER: GRANDMASTER FLASH."),
    ("portals", "DOES HE EVEN EXIST? I THOUGHT HE WAS A LEGEND."),
    ("bible", "IF WE CAN FIND HIM, YOU MUST SPRAY A PORTAL!"),
]
BACK_HOME = GameState(current_scene="hq", inventory=WITH_RECORD, rap_battle="won",
                      left_scenes=["hq", "block", "record_shop", "gate", "station"])
STUCK = GameState(current_scene="hq", inventory=WITH_RECORD, rap_battle="won", stuck=True,
                  left_scenes=["hq", "block", "record_shop", "gate", "station"])


def overlay_of(svg, action):
    """The data-overlay of the part around this data-action (the nearest one before it)."""
    at = svg.index(f'data-action="{action}"')
    return re.findall(r'data-overlay="([^"]*)"', svg[:at])[-1]


def clickable_box(svg, action):
    """The see-through rect that is clicked for this action: (x, y, width, height)."""
    part = svg[svg.index(f'data-action="{action}"'):]
    part = part[:part.index("</g>")]
    x, y, w, h = re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*fill="transparent"', part).groups()
    return float(x), float(y), float(w), float(h)


# --- the rules ---

def test_the_stuck_lines():
    assert SCENES["hq"]["dialogue_stuck"]["lines"] == STUCK_LINES


def test_the_crew_talks_once_needle_is_stuck():
    assert conversation(STUCK) == ("stuck", STUCK_LINES)
    assert conversation(BACK_HOME)[0] != "stuck"                          # not before he tried
    met = GameState(**{**STUCK.__dict__, "met_flash": True})
    assert conversation(met)[0] != "stuck"                                # not once they've met Flash


def test_the_rules_of_the_try_are_the_same():
    result = apply_action(BACK_HOME, "try_practice")
    assert result.accepted and result.state.stuck is True
    assert apply_action(BACK_HOME, "go_flash").accepted is False          # no portal before he tried
    assert apply_action(result.state, "go_flash").state.current_scene == "flash"


# --- in the app ---

def test_clicking_the_turntables_plays_the_try_first(db_file):
    save_game(db_file, BACK_HOME)
    at = start_app()
    choose(at, "resume")
    assert "try_practice" in picture(at)["enabled"]
    choose(at, "try_practice", screen="picture")                         # the turntables
    assert load_game(db_file).stuck is False                              # nothing saved yet
    assert picture(at)["enabled"] == ["decks_ready"]                      # he picks up the record
    choose(at, "decks_ready", screen="picture")                           # ... and he's behind the decks
    assert "trying" in picture(at)["show"] and picture(at)["enabled"] == ["tried"]
    assert at.session_state["audio"]["src"].endswith("audio/records/think_about_it_off.wav")
    assert load_game(db_file).stuck is False                              # still nothing saved
    assert svg_of(at) == "scene-hq"                                       # (not the practice screen)
    choose(at, "tried", screen="picture")                                 # 15 s later: it's always off
    assert load_game(db_file).stuck is True                               # now he's stuck, saved
    assert at.session_state["audio"]["cmd"] == "fade"
    for i in range(len(STUCK_LINES)):
        assert bubbles(at) == [f"stuck-{i}"]
        choose(at, "next", screen="picture")
    assert bubbles(at) == []
    assert "go_flash" in picture(at)["enabled"]                           # Portals' spray cans
    choose(at, "go_flash", screen="picture")
    assert at.session_state["walk"] == "assets/walks/hq__flash.svg"
    assert load_game(db_file).met_flash is True


def test_stopping_during_the_try_saves_nothing(db_file):
    save_game(db_file, BACK_HOME)
    at = start_app()
    choose(at, "resume")
    choose(at, "try_practice", screen="picture")
    choose(at, "decks_ready", screen="picture")
    at = start_app()                                                      # the app stops and starts again
    choose(at, "resume")
    assert load_game(db_file).stuck is False
    assert "try_practice" in picture(at)["enabled"] and "trying" not in picture(at)["show"]


def test_after_a_restart_while_stuck_the_crew_reminds_him(db_file):
    save_game(db_file, STUCK)
    at = start_app()
    choose(at, "resume")
    assert bubbles(at) == ["stuck-0"]


def svg_of(at):
    return re.search(r'<svg[^>]*id="([^"]+)"', picture(at)["svg"]).group(1)


# --- the pictures ---

def test_the_turntables_are_clicked_not_a_button():
    assert overlay_of(HQ, "try_practice") == "has-vinyl !stuck !practicing"
    assert overlay_of(HQ, "practice") == "met-flash !practiced !practicing"   # later, the real practice too
    for action in ("try_practice", "practice"):
        x, y, w, h = clickable_box(HQ, action)
        assert 255 <= x and x + w <= 470 and 255 <= y and y + h <= 315, action  # on the DJ table's turntables
    assert "PRACTICE THE BREAK" not in HQ and "PORTAL TO FLASH" not in HQ


def test_portals_spray_cans_open_the_portal():
    assert overlay_of(HQ, "go_flash") == "stuck"
    x, y, w, h = clickable_box(HQ, "go_flash")
    assert 640 <= x and x + w <= 760 and 200 <= y and y + h <= 380        # at Portals (x 700)


def test_the_try_in_the_picture():
    trying = HQ[HQ.index('data-overlay="practicing needle-busy trying"'):]
    trying = trying[:trying.index("<!-- end trying -->")]
    assert 'data-auto-action="tried"' in trying
    delay = float(re.search(r'data-auto-delay="([\d.]+)"', trying).group(1))
    assert 14 <= delay <= 17                                              # about 15 s
    assert trying.count("OFF!") >= 3


def test_the_stuck_bubbles_are_in_the_basement():
    for i, (speaker, line) in enumerate(STUCK_LINES):
        bubble = HQ[HQ.index(f'data-overlay="stuck-{i}"'):]
        bubble = bubble[:bubble.index("</g>")].replace("&#39;", "'")
        assert line.split()[0] in bubble, i


def test_the_off_break_sound():
    path = ROOT / "static" / SONGS["think_about_it_off"]["file"]
    with wave.open(str(path)) as w:
        secs = w.getnframes() / w.getframerate()
    assert 14 <= secs <= 17 and not SONGS["think_about_it_off"].get("loop")
    trying = HQ[HQ.index('data-overlay="practicing needle-busy trying"'):]
    delay = float(re.search(r'data-auto-delay="([\d.]+)"', trying).group(1))
    assert abs(delay - secs) < 1.0                                        # the picture goes on when it's over


def test_the_walk_through_the_portal():
    assert "YOU DID IT!" in TO_FLASH
    going_in = TO_FLASH[TO_FLASH.index('id="crew-into-portal"'):]
    going_in = going_in[:going_in.index("<!-- end crew-into-portal -->")]
    for who in ("Reekz", "Fantastic Needle", "Portals", "MC Bible"):
        assert f"<!-- {who}" in going_in, who
    assert re.search(r'<svg[^>]*data-auto-action="enter"', TO_FLASH)      # it still goes on by itself
