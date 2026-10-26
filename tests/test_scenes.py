import re
from pathlib import Path

import pytest

from art import build
from db import save_game
from db import load_game
from logic import GameState
from tests.apphelpers import act, choose, click, offered, picture, shows_picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
HQ = ROOT / "assets" / "scenes" / "hq.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def test_basement_picture_shows_the_story():
    # docs/story.md: the crate is empty, the Sopranos crossed out the GoodFellas piece,
    # Needle is furious, and the rhyme book is on the couch
    # (changed: the crossed-out piece replaces the sticker on the turntable)
    svg = HQ.read_text()
    assert 'id="scene-hq"' in svg
    for part in ('id="empty-crate"', 'id="sopranos-crossout"', 'id="turntables"', 'id="couch"',
                 'id="rhyme-book"', 'id="needle-furious"'):
        assert part in svg
    assert 'id="sopranos-sticker"' not in svg
    # the cover reads RHYME / BOOK on two lines
    book = svg[svg.index('id="rhyme-book"'):]
    book = book[:book.index("</g>")]
    assert ">RHYME</text>" in book and ">BOOK</text>" in book


# changed: Scorpio was swapped for CAN's Vitamin C
CLASSIC_BREAKS = ("APACHE", "FUNKY DRUMMER", "IT'S JUST BEGUN", "IMPEACH THE PRESIDENT", "VITAMIN C", "THE MEXICAN")


def test_sopranos_went_over_the_goodfellas_piece():
    svg = HQ.read_text()
    # the GoodFellas piece is still there underneath, so you can tell what it said
    goodfellas = svg.index(">GOODFELLAS</text>")
    crossout = svg.index('id="sopranos-crossout"')
    assert goodfellas < crossout  # the Sopranos painted on top of it
    over = svg[crossout:]
    over = over[:over.index("<!-- end sopranos-crossout -->")]
    assert ">SOPRANOS</text>" in over
    assert over.count('class="slash"') == 2  # two strokes crossing the name out


def test_basement_is_a_hip_hop_hq():
    svg = HQ.read_text()
    for part in ('id="checkerboard-floor"', 'id="soundsystem"', 'id="graffiti-corner"', 'id="vinyls"'):
        assert part in svg
    # changed: the checkerboard is only the little dance floor where Reekz breaks
    assert 'id="concrete-floor"' in svg
    floor = svg[svg.index('id="checkerboard-floor"'):]
    floor = floor[:floor.index("</g>")]
    xs = [float(v) for v in re.findall(r"(-?[\d.]+),[\d.]+", floor)]
    assert min(xs) > 420 and max(xs) < 800
    vinyls = svg[svg.index('id="vinyls"'):]
    vinyls = vinyls[:vinyls.index("<!-- end vinyls -->")]
    assert vinyls.count('class="record"') >= 8
    for title in CLASSIC_BREAKS:
        assert title in vinyls


def test_soundsystem_pumps():
    svg = HQ.read_text()
    system = svg[svg.index('id="soundsystem"'):]
    system = system[:system.index("<!-- end soundsystem -->")]
    assert 'type="scale"' in system  # the woofers pulse to the beat


def test_reekz_breaks_headspin_then_1990_in_a_loop():
    # changed: the windmill was removed; Reekz does a headspin and a 1990 now
    svg = HQ.read_text()
    assert "<!-- Reekz (breaking" in svg
    assert 'id="headspin"' in svg and 'id="nineteen-ninety"' in svg and 'id="windmill"' not in svg
    dance = svg[svg.index('id="reekz-breaking"'):]
    dance = dance[:dance.index("<!-- end reekz-breaking -->")]
    assert dance.count('repeatCount="indefinite"') >= 4  # both moves loop and take turns
    assert "#f4f4f4" in dance and "#c0392b" in dance  # still his white bucket hat and red tracksuit


def test_crew_tags_in_the_graffiti_corner():
    svg = HQ.read_text()
    corner = svg[svg.index('id="graffiti-corner"'):]
    corner = corner[:corner.index("<!-- end graffiti-corner -->")]
    assert "WILD" not in corner and "STYLE" not in corner
    for name in ("Needle", "Bible", "Portals", "Reekz"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert re.search(rf'class="tag"[^>]*>{name}', corner), name


def test_it_is_obvious_the_record_was_taken_from_the_crate():
    svg = HQ.read_text()
    sleeve = svg[svg.index('id="empty-sleeve"'):]
    sleeve = sleeve[:sleeve.index("<!-- end empty-sleeve -->")]
    assert "THINK ABOUT IT" in sleeve
    assert 'id="missing-record"' in sleeve and "stroke-dasharray" in sleeve


def test_headspin_and_1990_hand_over_smoothly():
    # changed: the windmill was removed; Reekz does a headspin and a 1990 now
    from art.crew import reekz_breaking
    dance = reekz_breaking(0, 0)
    for move in ("headspin", "nineteen-ninety"):
        part = dance[dance.index(f'id="{move}"'):]
        fade = part.split('attributeName="opacity"')[1].split("/>")[0]
        assert "discrete" not in fade  # a crossfade, not a cut
        assert len(fade.split('values="')[1].split('"')[0].split(";")) >= 5
        assert part.count('attributeName="d" values="') >= 6
        frames = part.split('attributeName="d" values="')[1].split('"')[0].split(";")
        assert len(frames) >= 37  # 36 frames per turn (+ back to the start): smooth


def test_reekz_spins_in_3d():
    # The spins are computed from a 3D skeleton: limbs move between frames (animated path data),
    # limbs swap in front of and behind his body, and his face only shows when he faces us.
    from art.crew import reekz_breaking
    dance = reekz_breaking(0, 0)
    for move in ("headspin", "nineteen-ninety"):
        part = dance[dance.index(f'id="{move}"'):]
        part = part[:part.index("<!-- end " + move + " -->")]
        assert part.count('attributeName="d"') >= 6           # limbs follow the 3D rotation
        assert 'class="front"' in part and 'class="back"' in part  # depth: in front of / behind the body
        assert 'id="' + move + '-face"' in part


def test_basement_conversation_has_a_bubble_per_line():
    # Changed: the bubbles are no longer timed; the player clicks through them (see below).
    from logic import SCENES
    svg = HQ.read_text()
    talk = svg[svg.index('id="dialogue"'):]
    talk = talk[:talk.index("<!-- end dialogue -->")]
    dialogue = SCENES["hq"]["dialogue"]
    for i, (speaker, line) in enumerate(dialogue):
        bubble = talk[talk.index(f'data-overlay="talk-{i}"'):]
        bubble = bubble[:bubble.index("</g>")]
        assert 'data-action="next"' in bubble
        for word in line.replace('"', "&quot;").split():
            assert word in bubble, (speaker, word)


def test_conversation_goes_on_with_each_click(db_file):
    from logic import SCENES
    # changed: the picture also shows other things now (e.g. the rhyme book still on the couch),
    # so this compares only the speech bubbles
    def talking(at):
        return [s for s in picture(at)["show"] if s.startswith("talk-")]

    at = start_app()
    start_new_game(at)
    assert talking(at) == ["talk-0"]
    for i in range(1, len(SCENES["hq"]["dialogue"])):
        choose(at, "next", screen="picture")
        assert talking(at) == [f"talk-{i}"]
    choose(at, "next", screen="picture")  # after the last line the conversation is over
    assert talking(at) == []
    assert at.session_state["game"].current_scene == "hq"


def test_basement_has_no_text_or_buttons_under_the_picture(db_file):
    at = start_app()
    start_new_game(at)
    assert len(at.main.header) == 0  # (the inventory in the sidebar stays)
    assert len(at.main.markdown) == 0
    assert len(at.main.button) == 0


def test_basement_ways_out_are_graffiti_buttons_in_the_picture(db_file):
    svg = HQ.read_text()
    assert 'data-action="go_block"' in svg and "HIT THE BLOCK" in svg
    # changed: the basement only leads to the block; Rico's is reached from the block
    assert 'data-action="go_record_shop"' not in svg
    at = start_app()
    start_new_game(at)
    assert "go_block" in picture(at)["enabled"] and "go_record_shop" not in picture(at)["enabled"]
    act(at, "go_block")
    assert at.session_state["game"].current_scene == "block"


@pytest.mark.parametrize("thing", ["rhyme_book", "empty_sleeve"])
def test_things_in_the_basement_can_be_clicked(db_file, thing):
    from logic import SCENES
    svg = HQ.read_text()
    assert f'data-action="inspect:{thing}"' in svg
    assert f'data-overlay="inspect-{thing}"' in svg
    info = SCENES["hq"]["things"][thing]
    # changed: the rhyme book is read, not listened to; the empty sleeve keeps its song slot
    assert ("read" in info) if thing == "rhyme_book" else ("song" in info)
    at = start_app()
    start_new_game(at)
    saved = load_game(db_file)
    choose(at, f"inspect:{thing}", screen="picture")
    assert f"inspect-{thing}" in picture(at)["show"]
    # changed: the rhyme book's sign has TAKE IT, READ IT and LEAVE IT (leaving it closes the sign)
    assert picture(at)["enabled"] == (["close", "take_rhyme_book", "read:rhyme_book"]
                                      if thing == "rhyme_book" else ["close"])
    assert load_game(db_file) == saved  # looking at something is not a move
    choose(at, "close", screen="picture")
    assert f"inspect-{thing}" not in picture(at)["show"]


def test_basement_has_the_whole_crew():
    svg = HQ.read_text()
    for member in ("Fantastic Needle", "MC Bible", "Portals", "Reekz"):  # changed: MC Meyhem left the crew (specs/remove-meyhem.md)
        assert f"<!-- {member}" in svg


def test_bible_does_not_hold_the_book_while_it_is_on_the_couch():
    # changed: the book can be taken now. While it's on the couch (offer-take_rhyme_book) Bible
    # doesn't hold it; once the crew has it (has-rhyme_book) he does, and the couch is empty.
    svg = HQ.read_text()
    couch = svg[svg.index('data-overlay="offer-take_rhyme_book"'):]
    assert ">RHYME</text>" in couch[:couch.index("<!-- end couch-book -->")]
    holding = svg[svg.index('data-overlay="has-rhyme_book"'):]
    assert ">RHYME</text>" in holding[:holding.index("<!-- end bible-book -->")]
    assert svg.count(">RHYME</text>") == 2


def test_basement_picture_after_the_intro(db_file):
    at = start_app()
    start_new_game(at)
    assert shows_picture(at, "scene-hq")


def test_basement_picture_after_resume(db_file):
    save_game(db_file, GameState(current_scene="hq", inventory=[]))
    at = start_app()
    choose(at, "resume")
    assert shows_picture(at, "scene-hq")


def test_walk_plays_instead_of_the_picture(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(at, "go_record_shop")
    assert shows_picture(at, "walk-block-record-shop")
    assert not shows_picture(at, "scene-block")


def test_coming_back_without_a_walk_shows_the_basement(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    assert not shows_picture(at, "scene-hq")  # the block has its own picture

    act(at, "go_hq")
    assert shows_picture(at, "scene-hq")


def test_basement_asset_matches_its_source():
    assert HQ.read_text() == build.hq_scene()


def test_the_1990_spins_on_one_hand():
    # changed: the windmill was removed; Reekz does a headspin and a 1990 now
    # a handstand on one hand: that hand stays put on the floor, the rest of him is above the floor
    # and upside down (feet higher than the head), and he turns all the way round
    import math
    from art.crew import _nineteen_ninety_world
    angles = []
    for k in range(48):
        joints = _nineteen_ninety_world(2 * math.pi * k / 48)
        assert joints["hand_r"] == (0, 0, 0)
        assert all(y > 0 for name, (_, y, _) in joints.items() if name != "hand_r")
        assert joints["foot_l"][1] > joints["head"][1] and joints["foot_r"][1] > joints["head"][1]
        x, _, z = joints["hip_l"]
        angles.append(math.atan2(z, x))
    assert len({round(a, 2) for a in angles}) == 48


def test_the_1990_has_knees_elbows_and_a_trail():
    # changed: the windmill was removed; Reekz does a headspin and a 1990 now
    from art.crew import reekz_breaking
    dance = reekz_breaking(0, 0)
    move = dance[dance.index('id="nineteen-ninety"'):dance.index("<!-- end nineteen-ninety -->")]
    assert move.count('attributeName="d" values="') >= 16  # 8 limb parts (upper and lower), each outlined
    frames = move.split('attributeName="d" values="')[1].split('"')[0].split(";")
    assert len(frames) == 49                              # 48 positions per turn, back to the start
    assert move.count('stroke-dasharray="4 7"') == 2      # the trail of both feet
