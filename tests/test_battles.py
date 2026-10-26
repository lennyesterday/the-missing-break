"""The rhyme book, the rap battle in the station, the DJ battle at Disco Fever and the endings."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game, save_game
from logic import CHOKED_MESSAGE, ENDINGS, SCENES, GameState
from tests.apphelpers import act, choose, home_screen, picture, shows_picture, start_app, start_new_game, svg_screen

ROOT = Path(__file__).parent.parent
BATTLE = ROOT / "assets" / "scenes" / "battle.svg"
LEGENDS = ROOT / "assets" / "endings" / "ending_legends.svg"
STATIC = ROOT / "assets" / "endings" / "ending_static.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def resume_at(db_file, scene, inventory):
    save_game(db_file, GameState(current_scene=scene, inventory=inventory))
    at = start_app()
    choose(at, "resume")
    return at


# --- the rhyme book ---

def test_taking_the_rhyme_book_from_the_couch(db_file):
    at = start_app()
    start_new_game(at)
    assert "offer-take_rhyme_book" in picture(at)["show"]
    choose(at, "inspect:rhyme_book", screen="picture")
    sign = part(picture(at)["svg"], 'data-overlay="inspect-rhyme_book"', "<!-- end sign -->")
    assert 'data-action="take_rhyme_book"' in sign and "TAKE IT" in sign

    choose(at, "take_rhyme_book", screen="picture")

    assert at.session_state["game"].inventory == ["rhyme_book"]
    assert load_game(db_file).inventory == ["rhyme_book"]
    shown = picture(at)
    assert "offer-take_rhyme_book" not in shown["show"]  # the couch is empty now
    assert "has-rhyme_book" in shown["show"]             # Bible holds it
    assert "done-take_rhyme_book" in shown["show"]       # "you got the rhyme book"


def test_bible_carries_his_book_everywhere_once_he_has_it():
    for path in ("assets/scenes/hq.svg", "assets/scenes/record_shop.svg", "assets/scenes/block.svg",
                 "assets/scenes/station.svg", "assets/scenes/battle.svg", "assets/walks/block__record_shop.svg"):
        svg = (ROOT / path).read_text()
        # changed: in the station his spot also empties while he's at the mic ("... !rapping-bible")
        assert re.search(r'data-overlay="has-rhyme_book[" ]', svg), path
        assert re.search(r'data-overlay="lacks-rhyme_book[" ]', svg), path


def test_the_walk_shows_bible_with_or_without_his_book(db_file):
    # changed: the basement only leads to the block; Rico's is reached from the block
    at = resume_at(db_file, "block", ["rhyme_book"])
    act(at, "go_record_shop")
    assert "has-rhyme_book" in picture(at)["show"]
    other = resume_at(db_file, "block", [])
    act(other, "go_record_shop")
    assert "lacks-rhyme_book" in picture(other)["show"]


# --- the rap battle ---

def test_round_2_needs_the_rhyme_book(db_file):
    # changed: Bible raps alone ("rap_battle"; round 1, Meyhem, is gone: specs/remove-meyhem.md); without
    # his rhyme book he is no longer turned down: he chokes, and the lost battle is saved
    save_game(db_file, GameState(current_scene="station", inventory=["service_key"]))
    at = start_app()
    choose(at, "resume")
    act(at, "rap_battle")
    assert "rapping-bible_chokes" in picture(at)["show"]  # his choke plays
    choose(at, "skip_verse", screen="picture")
    # changed: then it's game over (KRETE KEEPS THE CROWN)
    shown = svg_screen(at, "ending")
    assert shown is not None and CHOKED_MESSAGE.upper().replace('"', "&quot;")[:40] in shown["svg"]
    assert load_game(db_file) == GameState(current_scene="station", inventory=["service_key"],
                                           ending="ending_lost_battle", rap_battle="lost")


def test_round_2_wins_the_record(db_file):
    # changed: Bible raps alone ("rap_battle", was "bible_finishes" after Meyhem), specs/remove-meyhem.md
    save_game(db_file, GameState(current_scene="station", inventory=["rhyme_book", "service_key"]))
    at = start_app()
    choose(at, "resume")
    assert "lacks-vinyl" in picture(at)["show"]  # Krete still has it
    act(at, "rap_battle")
    shown = picture(at)
    assert at.session_state["game"].inventory == ["rhyme_book", "service_key", "vinyl"]
    assert "done-rap_battle" in shown["show"]
    assert "has-vinyl" in shown["show"] and "lacks-vinyl" not in shown["show"]
    assert "rap_battle" not in shown["enabled"]


def test_the_station_shows_both_rounds():
    svg = (ROOT / "assets" / "scenes" / "station.svg").read_text()
    # changed: who goes first is chosen; the outcomes come up when the rapping is over
    # changed: without the rhyme book Bible chokes (it used to be turned down: "rejected-...")
    # changed: losing goes to the game-over screen, so only the winning steps have a sign here
    # changed: one round, Bible alone (specs/remove-meyhem.md)
    for overlay in ("done-rap_battle !rapping", "lacks-vinyl", "has-vinyl"):
        assert f'data-overlay="{overlay}"' in svg


# --- Disco Fever ---

def test_disco_fever_from_the_block(db_file):
    at = resume_at(db_file, "block", [])
    assert "go_battle" in picture(at)["enabled"]
    assert "BOROUGH DJ BATTLE" in picture(at)["svg"]  # changed: renamed from DISCO FEVER (product owner)
    act(at, "go_battle")
    assert shows_picture(at, "scene-battle")
    assert {"start_battle", "next"} <= set(picture(at)["enabled"])


def test_the_club():
    svg = BATTLE.read_text()
    assert 'id="scene-battle"' in svg
    for p in ('id="disco-ball"', 'id="light-spots"', 'id="crowd"', 'id="dj-booth"'):
        assert p in svg
    assert 'data-action="start_battle"' in svg and "START THE BATTLE" in svg
    for i in range(len(SCENES["battle"]["dialogue"])):
        assert f'data-overlay="talk-{i}"' in svg


@pytest.mark.parametrize("inventory, practiced, ending", [
    (["rhyme_book", "service_key", "vinyl"], True, "ending_legends"),  # changed: and he practiced
    (["rhyme_book", "service_key", "vinyl"], False, "ending_out_of_practice"),  # changed: the plot twist
    ([], False, "ending_static"),
])
def test_the_battle_ends(db_file, inventory, practiced, ending):
    save_game(db_file, GameState(current_scene="battle", inventory=inventory, practiced=practiced))
    at = start_app()
    choose(at, "resume")
    act(at, "start_battle")

    assert at.session_state["game"].ending == ending
    assert load_game(db_file).ending == ending
    shown = svg_screen(at, "ending")
    assert shown is not None and f'id="{ending.replace("_", "-")}"' in shown["svg"]
    assert shown["enabled"] == ["to_start"]
    assert picture(at) is None  # no more story actions (PT05)


def test_an_ending_can_be_seen_again_and_the_game_started_over(db_file):
    save_game(db_file, GameState(current_scene="battle", inventory=[], ending="ending_static"))
    at = start_app()
    choose(at, "resume")
    assert svg_screen(at, "ending") is not None  # review the outcome
    choose(at, "to_start", screen="ending")
    assert home_screen(at) is not None           # back to the start: START asks before replacing it
    choose(at, "start")
    assert home_screen(at)["show"] == ["confirm-restart"]


@pytest.mark.parametrize("path, ending", [(LEGENDS, "ending_legends"), (STATIC, "ending_static"),
                                          (ROOT / "assets" / "endings" / "ending_out_of_practice.svg", "ending_out_of_practice"),
                                          (ROOT / "assets" / "endings" / "ending_lost_battle.svg", "ending_lost_battle")])
def test_each_ending_is_clearly_identified(path, ending):
    # changed: and the game over after a lost rap battle, whose button is RESTART
    svg = path.read_text()
    assert ENDINGS[ending]["title"].upper() in svg
    assert 'data-action="restart"' in svg if ending == "ending_lost_battle" else 'data-action="to_start"' in svg
    words = ENDINGS[ending]["text"].replace('"', "&quot;").upper().split()
    for word in words:
        assert word in svg.upper(), word


def test_the_legends_ending_has_the_whole_party():
    svg = LEGENDS.read_text()
    assert "<!-- Reekz (breaking" in svg           # Reekz goes down to the real break
    assert 'id="spinning-record"' in svg and "THINK" in svg
    assert 'id="portal-backdrop"' in svg           # Portals' backdrop, another dimension
    assert svg.count("<!-- MC Bible") >= 1         # changed: Bible on the mic (Meyhem left the crew)


def test_the_static_ending_is_flat():
    svg = STATIC.read_text()
    assert "<!-- Reekz (" in svg and "<!-- Reekz (breaking" not in svg  # he stays standing
    assert "SOPRANOS" in svg                        # they take the crown


@pytest.mark.parametrize("asset, make", [
    ("assets/scenes/battle.svg", build.battle_scene),
    ("assets/endings/ending_legends.svg", build.ending_legends),
    ("assets/endings/ending_static.svg", build.ending_static),
    ("assets/endings/ending_lost_battle.svg", build.ending_lost_battle),
    ("assets/endings/ending_out_of_practice.svg", build.ending_out_of_practice),
])
def test_assets_match_their_source(asset, make):
    assert (ROOT / asset).read_text() == make()


def test_walking_the_whole_win_path_in_the_app(db_file):
    # A5, in the app: from a new game to the legends
    at = start_app()
    start_new_game(at)
    choose(at, "inspect:rhyme_book", screen="picture")
    choose(at, "take_rhyme_book", screen="picture")
    act(at, "go_block")  # changed: the basement only leads to the block; Rico's is reached from the block
    act(at, "go_record_shop")
    act(at, "enter")
    act(at, "take_service_key")
    act(at, "go_block")
    act(at, "go_gate")  # changed: the crew walks to the station gate first
    act(at, "enter_station")  # with the key: the gate opens
    act(at, "enter")  # changed: ENTER THE STATION leads in
    act(at, "rap_battle")  # changed: Bible raps alone (specs/remove-meyhem.md)
    act(at, "go_block")
    act(at, "go_hq")       # changed: the plot twist: back to the basement to practice
    # changed: he can't catch the break; Portals' portal to Grandmaster Flash ("the secret lies in the crayon")
    act(at, "try_practice")
    act(at, "go_flash")
    act(at, "go_hq")
    act(at, "go_block")
    # changed: Reekz wins the cypher ($10), the corner store sells crayons
    from tests.test_cypher_battle import play_set
    choose(at, "inspect:cypher", screen="picture")
    choose(at, "join:cypher", screen="picture")
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["toprock", "helicopter", "headspin", "freeze"])
    choose(at, "next_round", screen="cypher")
    choose(at, "reekz_turn", screen="cypher")
    play_set(at, ["helicopter", "nineteen_ninety", "freeze"])
    choose(at, "leave_cypher", screen="cypher")
    act(at, "go_store")
    act(at, "buy_crayons")
    act(at, "go_block")
    act(at, "go_hq")
    choose(at, "practice", screen="picture")
    choose(at, "decks_ready", screen="picture")  # changed: Needle goes behind the decks, marks the break, keeps it going
    for _ in range(2):  # changed: two marks (it was three); each time he stops the record, marks it, lets go
        choose(at, "mark_hit", screen="crayon")
        choose(at, "mark_done", screen="crayon")
    for _ in range(4):  # changed: four clean switches (it was three)
        choose(at, "loop_hit", screen="practice")
    act(at, "go_block")
    act(at, "go_battle")
    act(at, "start_battle")
    assert load_game(db_file).ending == "ending_legends"


# --- Bible's verse in round 2: he walks to the mic, the underground crowd goes wild ---

STATION = ROOT / "assets" / "scenes" / "station.svg"


def test_the_crowd_sits_on_and_in_the_train():
    # changed: the crowd used to be silhouettes on the platform; now they are characters like the
    # crew, sitting on the roof of the abandoned car, looking out of its windows, in its open doors
    svg = STATION.read_text()
    assert 'id="underground-crowd"' not in svg
    inside = part(svg, 'id="train-crowd"', "<!-- end train-crowd -->")
    assert inside.count('class="spectator"') >= 7
    assert inside.count('class="open-door"') == 2
    roof = part(svg, 'id="car-roof-crowd"', "<!-- end car-roof-crowd -->")
    assert roof.count('class="spectator"') >= 4
    for crowd in (inside, roof):
        assert crowd.count('class="eye"') >= 2 * crowd.count('class="spectator"')  # faces, not silhouettes


def test_the_crowd_cheers_when_bible_raps():
    # changed: their own arms go up (out of the windows, the doors and on the roof), while anyone raps
    svg = STATION.read_text()
    for crowd_id, end in (("train-crowd", "<!-- end train-crowd -->"), ("car-roof-crowd", "<!-- end car-roof-crowd -->")):
        crowd = part(svg, f'id="{crowd_id}"', end)
        # changed: they cheer for a verse ("cheering"), not when Bible chokes
        assert crowd.count('data-overlay="cheering"') >= 4      # arms up
        assert crowd.count('data-overlay="!cheering"') >= 4     # arms down


def test_a_battle_dj_provides_the_beats():
    svg = STATION.read_text()
    dj = part(svg, 'id="battle-dj"', "<!-- end battle-dj -->")
    assert "<!-- Battle DJ" in dj
    assert dj.count('class="turntable"') == 2
    assert 'id="scratch-hand"' in dj and 'type="rotate"' in dj           # the record spins
    assert 'id="headphones"' in dj


def test_a_mic_stand_waits_in_the_middle():
    svg = STATION.read_text()
    stand = part(svg, 'id="mic-stand"', "<!-- end mic-stand -->")
    assert 'data-overlay="!rapping"' in stand  # changed: the mic is gone from the stand while anyone raps


def test_round_2_bible_walks_to_the_mic_and_raps():
    svg = STATION.read_text()
    show = part(svg, 'id="bible-performs"', "<!-- end bible-performs -->")
    # changed: he performs while he raps ("rapping-bible"), not only after round 2
    assert 'data-overlay="rapping-bible"' in svg[svg.index('id="bible-performs"') - 80:svg.index('id="bible-performs"')]
    assert 'id="bibleIn"' in show and 'begin="indefinite"' in show       # starts when the round is won
    assert "<!-- MC Bible (black leather jacket, rhyme book)" in show     # walking forward
    assert 'begin="bibleIn.begin"' in show
    assert "<!-- MC Bible (on the mic" in show                           # then on the mic
    assert 'to="visible" begin="bibleIn.begin+2s"' in show


def test_bibles_spot_is_empty_while_he_raps():
    svg = STATION.read_text()
    # changed: while he is at the mic, rapping or choking (was !done-rap_round_2)
    assert 'data-overlay="has-rhyme_book !mic-bible"' in svg
    assert 'data-overlay="lacks-rhyme_book !mic-bible"' in svg


def test_the_page_can_hide_parts_and_start_animations_when_shown():
    app = (ROOT / "app.py").read_text()
    assert 'startsWith("!")' in app      # "!name" hides a part while name is shown
    assert "beginElement" in app         # animations marked begin="indefinite" start when shown
