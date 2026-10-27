"""Additional little conversations and scenes (specs/additional-little-conversations-and-scenes.md):
from Grandmaster Flash to the DJ battle the crew talks at each step, plus the LOOPED! piece,
Needle's "CRAYOLA, BABY!" and King Krete outside the Borough DJ Battle."""

import re
from pathlib import Path

import pytest

from db import load_game, save_game
from logic import SCENES, WALK_LINES, WALK_LINES_WHEN_HAS, GameState, conversation
from tests.apphelpers import act, choose, picture, start_app

ROOT = Path(__file__).parent.parent
WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]
LEFT = ["hq", "block", "record_shop", "gate", "station"]
AFTER_FLASH = dict(inventory=WITH_RECORD, rap_battle="won", stuck=True, met_flash=True, left_scenes=LEFT + ["flash"])

FROM_FLASH = [
    ("portals", "YO... DID THAT JUST HAPPEN? WE WERE IN OUTER SPACE!"),
    ("reekz", "GRANDMASTER FLASH IS REAL, AND HE PUT US ON!"),
    ("needle", "A CRAYON. ALL THESE YEARS AND THE SECRET IS A CRAYON."),
    ("bible", "THEN LET'S GET ONE. TO THE BLOCK!"),
]
CYPHER = [
    ("reekz", "LOOK, THE CYPHER'S GOING ON IN FRONT OF THE CORNER STORE!"),
    ("portals", "THEY PASS THE HAT FOR WHOEVER WINS."),
    ("reekz", "HOLD MY GHETTOBLASTER. I'M GETTING US THAT CRAYON MONEY."),
]
CYPHER_WON = [
    ("bible", "REEKZ, YOU ATE THOSE B-BOYS ALIVE!"),
    ("reekz", "WINDMILL, FREEZE, DONE. TEN BUCKS, BABY."),
    ("needle", "THAT'S CRAYON MONEY. CORNER STORE, LET'S GO!"),
]
BUYING = [
    ("clerk", "WHAT'LL IT BE, FELLAS? CASH ONLY."),
    ("needle", "ONE BOX OF CRAYONS, PLEASE."),
    ("clerk", "CRAYONS? YOU BOYS GOING BACK TO SCHOOL?"),
    ("portals", "NAH. WE'RE GOING TO THE BOROUGH DJ BATTLE."),  # (renamed from the Borough DJ Battle, by the product owner)
]
BROKE = [
    ("clerk", "NO MONEY, NO CRAYONS. COME BACK WITH CASH."),
    ("reekz", "BET. THE CYPHER'S RIGHT OUTSIDE."),
]
BLOCK_CRAYONS = [
    ("needle", "GOT THE CRAYONS. NOW BACK TO THE DECKS!"),  # (only Needle: Bible's line was taken out, product owner)
]
HQ_CRAYONS = [
    ("needle", "OKAY, FLASH. LET'S SEE IF YOUR CRAYON WORKS."),
    ("portals", "MARK IT LIKE A TAG, NEEDLE. RIGHT WHERE IT STARTS OVER."),
]
LOOPED = [
    ("needle", "I GOT IT! THE BREAK, IT'S LOOPING!"),
    ("reekz", "THAT'S THE ONE! I COULD BREAK TO THAT ALL NIGHT!"),
    ("bible", "FLASH WAS RIGHT. STOP LISTENING, LOOK."),
    ("portals", "THEN WHAT ARE WE WAITING FOR? THE BOROUGH DJ BATTLE!"),
]
FINAL = [
    ("reekz", "THIS IS IT, GOODFELLAS. THE BOROUGH FINAL."),
    ("needle", "THE SOPRANOS TOOK MY BREAK. TONIGHT I TAKE THEIR CROWN."),
    ("bible", "LET'S GO SHOW THE BRONX WHO WE ARE."),
]
MOMENTS = [("hq", "from_flash", FROM_FLASH), ("block", "cypher", CYPHER), ("block", "cypher_won", CYPHER_WON),
           ("corner_store", "buying", BUYING), ("corner_store", "broke", BROKE), ("block", "crayons", BLOCK_CRAYONS),
           ("hq", "crayons", HQ_CRAYONS), ("hq", "looped", LOOPED), ("block", "final", FINAL)]


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def state(scene, **changes):
    return GameState(current_scene=scene, **{**AFTER_FLASH, **changes})


def moment(scene, kind):
    return next(m for m in SCENES[scene]["moments"] if m["kind"] == kind)


def bubbles(at):
    return [s for s in picture(at)["show"] if re.fullmatch(r"[a-z_]+-\d+", s) and not s.startswith(("has-", "lacks-", "battle-", "offer-", "done-", "rejected-"))]


def click_through(at, kind, lines, start=0):
    for i in range(start, len(lines)):
        assert bubbles(at) == [f"{kind}-{i}"], (kind, i, bubbles(at))
        choose(at, "next", screen="picture")


# --- the rules ---

@pytest.mark.parametrize("scene, kind, lines", MOMENTS)
def test_the_lines(scene, kind, lines):
    assert moment(scene, kind)["lines"] == lines


@pytest.mark.parametrize("game, came_from, just_did, expected", [
    (state("hq"), "flash", None, "from_flash"),
    (state("hq"), None, None, None),                                                   # (after a restart: not)
    (state("block"), "hq", None, "cypher"),
    (state("block", money=1000), "hq", None, None),                                    # not with money
    (state("block", money=1000), None, "win_cypher", "cypher_won"),
    (state("corner_store", money=1000), "block", None, "buying"),
    (state("corner_store"), "block", None, "broke"),
    (state("corner_store", inventory=WITH_RECORD + ["crayons"]), "block", None, None),  # broke, but has them
    (GameState(current_scene="corner_store"), "block", None, None),                   # before Flash: the clerk's usual line
    (state("block", inventory=WITH_RECORD + ["crayons"], money=900), "corner_store", None, "crayons"),
    (state("hq", inventory=WITH_RECORD + ["crayons"], money=900), "block", None, "crayons"),
    (state("hq", inventory=WITH_RECORD + ["crayons"], money=900, practiced=True), None, "practice", "looped"),
    (state("hq", inventory=WITH_RECORD + ["crayons"], money=900, practiced=True), "block", None, None),
    (state("block", inventory=WITH_RECORD + ["crayons"], money=900, practiced=True), "hq", None, "final"),
    (state("block", inventory=WITH_RECORD + ["crayons"], money=900, practiced=True), "corner_store", None, None),
])
def test_each_moment_comes_when_it_fits(game, came_from, just_did, expected):
    kind, _ = conversation(game, came_from=came_from, just_did=just_did)
    if expected:
        assert kind == expected
    else:
        assert kind not in {k for _, k, _ in MOMENTS}


def test_the_earlier_conversations_come_first():
    stuck = GameState(current_scene="hq", inventory=WITH_RECORD, rap_battle="won", stuck=True, left_scenes=LEFT)
    assert conversation(stuck)[0] == "stuck"
    won = GameState(current_scene="block", inventory=WITH_RECORD, rap_battle="won", left_scenes=LEFT)
    assert conversation(won, came_from="station")[0] == "won"


# --- in the app: from Flash to the Borough DJ Battle ---

def test_the_whole_way_from_flash_to_disco_fever(db_file):
    save_game(db_file, state("flash"))
    at = start_app()
    choose(at, "resume")
    for _ in SCENES["flash"]["dialogue"]:
        choose(at, "next", screen="picture")
    act(at, "go_hq")                                   # through the portal, back to the basement
    click_through(at, "from_flash", FROM_FLASH)
    act(at, "go_block")
    click_through(at, "cypher", CYPHER)
    act(at, "go_store")                                # broke
    click_through(at, "broke", BROKE)
    act(at, "go_block")
    assert bubbles(at) == []                           # (the cypher talk was once)
    from tests.test_cypher_battle import play_set
    choose(at, "inspect:cypher", screen="picture")
    choose(at, "join:cypher", screen="picture")
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["toprock", "helicopter", "headspin", "freeze"])
    choose(at, "next_round", screen="cypher")
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["helicopter", "nineteen_ninety", "freeze"])
    choose(at, "leave_cypher", screen="cypher")
    click_through(at, "cypher_won", CYPHER_WON)
    act(at, "go_store")
    assert bubbles(at) == ["buying-0"]
    choose(at, "next", screen="picture")
    act(at, "buy_crayons")                             # buying in the middle of it: the talk goes on
    click_through(at, "buying", BUYING, start=1)
    act(at, "go_block")
    click_through(at, "crayons", BLOCK_CRAYONS)
    act(at, "go_hq")
    click_through(at, "crayons", HQ_CRAYONS)
    choose(at, "practice", screen="picture")
    choose(at, "decks_ready", screen="picture")
    for _ in range(2):
        choose(at, "mark_hit", screen="crayon")
        choose(at, "mark_done", screen="crayon")
    for _ in range(4):
        choose(at, "loop_hit", screen="practice")
    assert load_game(db_file).practiced is True
    click_through(at, "looped", LOOPED)
    assert "practiced" in picture(at)["show"]          # LOOPED! on the wall
    act(at, "go_block")
    click_through(at, "final", FINAL)
    assert bubbles(at) == []
    assert load_game(db_file).current_scene == "block"   # talking saved nothing else


def test_after_a_restart_the_moments_that_depend_on_the_way_dont_come(db_file):
    save_game(db_file, state("hq", inventory=WITH_RECORD + ["crayons"], money=900, practiced=True))
    at = start_app()
    choose(at, "resume")
    assert bubbles(at) == []                            # no "looped" (it was before the restart)


# --- the pictures ---

@pytest.mark.parametrize("scene, kind, lines", MOMENTS)
def test_the_bubbles_are_in_the_pictures(scene, kind, lines):
    svg = (ROOT / "assets" / "scenes" / f"{scene}.svg").read_text()
    for i, (_, line) in enumerate(lines):
        bubble = svg[svg.index(f'data-overlay="{kind}-{i}"'):]
        bubble = bubble[:bubble.index("</g>")].replace("&#39;", "'").replace("&amp;", "&")
        assert line.split()[0] in bubble, (kind, i)


def test_no_ready_for_the_final_sign_any_more():
    hq = (ROOT / "assets" / "scenes" / "hq.svg").read_text()
    assert "READY FOR THE FINAL!" not in hq


def test_looped_on_the_basement_wall():
    hq = (ROOT / "assets" / "scenes" / "hq.svg").read_text()
    piece = hq[hq.index('id="looped-piece"'):]
    assert 'data-overlay="practiced"' in hq[hq.rindex("<g", 0, hq.index('id="looped-piece"')) - 80:hq.index('id="looped-piece"')]
    assert "LOOPED!" in piece[:4000]


def test_crayola_baby_on_the_way_back_from_the_store():
    assert WALK_LINES["corner_store__block"] == [("needle", "CRAYOLA, BABY!", WALK_LINES["corner_store__block"][0][2])]
    assert WALK_LINES_WHEN_HAS["corner_store__block"] == "crayons"
    walk = (ROOT / "assets" / "walks" / "corner_store__block.svg").read_text()
    bubble = walk[walk.index("<title>Needle: CRAYOLA, BABY!</title>") - 300:]
    assert 'data-overlay="has-crayons"' in bubble[:300]


def test_krete_outside_disco_fever():
    # changed (specs/final-voices.md): the bouncer's line is a walk line too now, after Krete's
    (speaker, line, _), _ = WALK_LINES["block__battle"]
    assert (speaker, line) == ("krete", "BACK FOR MORE, GOODFELLAS? DIDN'T LEARN THE FIRST TIME?")
    walk = (ROOT / "assets" / "walks" / "block__battle.svg").read_text()
    assert "<!-- King Krete" in walk and "<title>King Krete: BACK FOR MORE" in walk


def test_the_walk_lines_are_spoken_only_with_what_they_need(db_file):
    save_game(db_file, state("corner_store", money=1000))
    at = start_app()
    choose(at, "resume")
    choose(at, "go_block", screen="picture")            # without crayons: Needle says nothing
    assert picture(at)["voice"] is None


# --- the voices (the product owner's recordings) ---

RECORDED = [("hq/from_flash", FROM_FLASH), ("hq/looped", LOOPED), ("hq/crayons", HQ_CRAYONS),
            ("corner_store/buying", BUYING), ("block/cypher", CYPHER), ("block/cypher_won", CYPHER_WON),
            ("block/crayons", BLOCK_CRAYONS), ("block/final", FINAL)]  # changed: block/final recorded (specs/final-voices.md)
NOT_RECORDED_YET = [("corner_store/broke", BROKE)]
VOICES = ROOT / "static" / "audio" / "voices"


@pytest.mark.parametrize("folder, lines", RECORDED)
def test_the_recorded_conversations(folder, lines):
    for i, (speaker, _) in enumerate(lines):
        assert (VOICES / folder / f"{i:02d}_{speaker}.mp3").is_file(), (folder, i, speaker)


def test_the_clerks_first_line_is_spoken_too():
    assert SCENES["corner_store"]["dialogue"][0] == BUYING[0]  # the same words, the same recording
    assert (VOICES / "corner_store" / "00_clerk.mp3").is_file()


def test_back_from_flash_the_crew_speaks(db_file):
    save_game(db_file, state("flash"))
    at = start_app()
    choose(at, "resume")
    for _ in SCENES["flash"]["dialogue"]:
        choose(at, "next", screen="picture")
    act(at, "go_hq")
    for i, (speaker, _) in enumerate(FROM_FLASH):
        assert picture(at)["voice"]["src"] == f"app/static/audio/voices/hq/from_flash/{i:02d}_{speaker}.mp3"
        choose(at, "next", screen="picture")


def test_the_store_speaks(db_file):
    save_game(db_file, state("block", money=1000))
    at = start_app()
    choose(at, "resume")
    act(at, "go_store")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/corner_store/buying/00_clerk.mp3"
