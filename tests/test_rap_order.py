"""Who goes first in the rap battle: Meyhem has to go first, Bible finishes Krete. If Bible goes
first, Meyhem's bars after him don't hit as hard: the battle is lost for good, Krete keeps the
record and the game can only end in the static. Verses can be skipped and stop when the crew
leaves the station."""

import re
import sqlite3
from pathlib import Path

import pytest

from db import load_game, save_game
import logic
from logic import (CHOKED_MESSAGE, ENDINGS, LOST_BATTLE_MESSAGE, RAPPERS, SCENES, SONGS, GameState, apply_action,
                   available_actions, new_game, what_happens)
from tests.apphelpers import act, choose, intro_screen, picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
STATION = (ROOT / "assets" / "scenes" / "station.svg").read_text()
APP = (ROOT / "app.py").read_text()


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def in_station(inventory=("service_key",), rap_battle=None):
    return GameState(current_scene="station", inventory=list(inventory), rap_battle=rap_battle)


def ids(state):
    return [a["id"] for a in available_actions(state)]


def action(action_id):
    return next(a for a in SCENES["station"]["actions"] if a["id"] == action_id)


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


# --- the rules ---

def test_a_new_game_has_not_battled_yet():
    assert new_game().rap_battle is None


def test_the_player_chooses_who_goes_first():
    assert {"meyhem_first", "bible_first", "go_block"} == set(ids(in_station()))


def test_meyhem_first_is_remembered_and_bible_can_finish():
    result = apply_action(in_station(), "meyhem_first")
    assert result.accepted
    assert result.state.rap_battle == "meyhem_went_first"
    assert result.state.inventory == ["service_key"]
    assert set(ids(result.state)) == {"bible_finishes", "go_block"}  # the order is decided


def test_without_his_rhyme_book_bible_chokes_and_the_battle_is_lost():
    # changed: Bible without his rhyme book used to be turned down (nothing changed); now he goes
    # up anyway, chokes, forgets his bars, the crowd boos him off: lost for good
    state = in_station(rap_battle="meyhem_went_first")
    result = apply_action(state, "bible_finishes")
    assert result.accepted and result.message == CHOKED_MESSAGE
    assert result.state.rap_battle == "lost"
    assert "vinyl" not in result.state.inventory
    assert result.state.ending == "ending_lost_battle"  # changed: game over right away (was: back to the block)
    assert ids(result.state) == []


def test_meyhem_then_bible_wins_the_record():
    state = in_station(("rhyme_book", "service_key"), "meyhem_went_first")
    result = apply_action(state, "bible_finishes")
    assert result.accepted
    assert result.state.inventory == ["rhyme_book", "service_key", "vinyl"]
    assert result.state.rap_battle == "won"
    assert ids(result.state) == ["go_block"]


def test_bible_first_without_his_rhyme_book_chokes_too():
    # changed: it used to be turned down; now he chokes and the battle is lost
    result = apply_action(in_station(), "bible_first")
    assert result.accepted and result.message == CHOKED_MESSAGE
    # changed: game over right away (it used to go on, without a way to win)
    assert result.state.rap_battle == "lost" and result.state.ending == "ending_lost_battle"
    assert ids(result.state) == []


def test_what_happens_says_who_raps():
    # with the book: his verse; without it: he chokes
    assert what_happens(in_station(("rhyme_book",)), "bible_first")["raps"] == ["bible", "meyhem"]
    assert what_happens(in_station(), "bible_first")["raps"] == ["bible_chokes"]
    assert what_happens(in_station(), "bible_first")["done"] == "bible_chokes"
    assert what_happens(in_station(rap_battle="meyhem_went_first"), "bible_finishes")["raps"] == ["bible_chokes"]
    assert what_happens(in_station(), "meyhem_first")["raps"] == ["meyhem"]
    assert what_happens(in_station(), "bible_finishes") is None  # not offered yet


def test_bible_first_loses_the_battle_for_good():
    result = apply_action(in_station(("rhyme_book", "service_key")), "bible_first")
    assert result.accepted
    assert result.message == LOST_BATTLE_MESSAGE
    assert result.state.rap_battle == "lost"
    assert "vinyl" not in result.state.inventory
    assert result.state.ending == "ending_lost_battle"  # changed: game over right away
    assert ids(result.state) == []  # no second try


def test_after_losing_the_battle_the_game_is_over():
    # changed: it used to go on (only to end in the static at Disco Fever); now the game is over
    # right there and the player has to start again
    result = apply_action(in_station(("rhyme_book", "service_key")), "bible_first")
    assert result.state.ending == "ending_lost_battle"
    assert not apply_action(result.state, "go_block").accepted
    assert ENDINGS["ending_lost_battle"]["title"] == "Krete Keeps the Crown"


def test_who_raps_in_each_choice():
    # Bible first: his verse, then Meyhem's bars after him
    assert action("meyhem_first")["raps"] == ["meyhem"]
    assert action("bible_first")["raps"] == ["bible", "meyhem"]
    assert action("bible_finishes")["raps"] == ["bible"]
    # changed: and Bible choking without his book (its recording comes from Suno)
    assert RAPPERS == {"meyhem": "mc_meyhem_verse", "bible": "mc_bible_verse", "bible_chokes": "mc_bible_chokes"}
    assert SONGS["mc_bible_chokes"]["file"] == "audio/mc_bible_chokes.mp3"
    assert (ROOT / "static" / "audio" / "mc_bible_chokes.mp3").is_file()  # recorded with Suno
    assert "mc_bible_chokes.mp3" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()
    assert (ROOT / "static" / SONGS["mc_meyhem_verse"]["file"]).is_file()
    assert "MC Meyhem" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()


def test_the_crew_hints_that_meyhem_goes_first():
    lines = " ".join(line for _, line in SCENES["station"]["dialogue"])
    assert "I'LL GO FIRST" in lines and "FINISH HIM" in lines


# --- saving ---

def test_the_battle_is_saved(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, in_station(rap_battle="lost"))
    assert load_game(path).rap_battle == "lost"


def test_older_saves_load_without_a_battle(tmp_path):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE save (id INTEGER PRIMARY KEY CHECK (id = 1), current_scene TEXT NOT NULL,"
                     " inventory TEXT NOT NULL, ending TEXT)")
        conn.execute("INSERT INTO save VALUES (1, 'station', '[\"service_key\"]', NULL)")
    assert load_game(path) == in_station()


# --- in the app ---

def resume_at(db_file, state):
    save_game(db_file, state)
    at = start_app()
    choose(at, "resume")
    return at


def test_meyhem_raps_and_can_be_skipped(db_file):
    at = resume_at(db_file, in_station())
    act(at, "meyhem_first")
    shown = picture(at)
    assert shown["audio"]["src"] == f"app/static/{SONGS['mc_meyhem_verse']['file']}"
    assert shown["audio"]["end"] == "verse_over"         # the page says when the verse is over
    assert {"rapping", "rapping-meyhem"} <= set(shown["show"])
    assert {"skip_verse", "go_block"} <= set(shown["enabled"])
    assert load_game(db_file).rap_battle == "meyhem_went_first"

    choose(at, "skip_verse", screen="picture")
    shown = picture(at)
    assert shown["audio"]["src"] is None                    # the verse stops
    assert "rapping" not in shown["show"]
    assert "done-meyhem_first" in shown["show"]             # and what happened comes up
    assert load_game(db_file).rap_battle == "meyhem_went_first"  # skipping changes nothing


def test_bible_first_plays_both_verses_one_after_the_other(db_file):
    at = resume_at(db_file, in_station(("rhyme_book", "service_key")))
    act(at, "bible_first")
    assert picture(at)["audio"]["src"] == f"app/static/{SONGS['mc_bible_verse']['file']}"
    assert "rapping-bible" in picture(at)["show"]
    choose(at, "verse_over", screen="picture")              # Bible's verse is over: Meyhem's bars after him
    assert picture(at)["audio"]["src"] == f"app/static/{SONGS['mc_meyhem_verse']['file']}"
    assert "rapping-meyhem" in picture(at)["show"]
    choose(at, "verse_over", screen="picture")
    # changed: when the rapping is over, the game-over screen comes (it used to stay in the station)
    assert picture(at) is None and svg_screen(at, "ending") is not None
    assert load_game(db_file).ending == "ending_lost_battle"


def test_leaving_the_station_stops_the_verse(db_file):
    at = resume_at(db_file, in_station())
    act(at, "meyhem_first")
    act(at, "go_block")
    shown = picture(at)
    assert shown["audio"]["src"] is None
    assert "rapping" not in shown["show"]
    assert load_game(db_file).current_scene == "block"


def test_the_battle_state_is_in_the_picture(db_file):
    assert "battle-open" in picture(resume_at(db_file, in_station()))["show"]
    assert "battle-meyhem_went_first" in picture(resume_at(db_file, in_station(rap_battle="meyhem_went_first")))["show"]


def test_lost_means_game_over_and_restart_starts_again_from_the_intro(db_file):
    lost = GameState(current_scene="station", inventory=["service_key"], ending="ending_lost_battle", rap_battle="lost")
    at = resume_at(db_file, lost)
    shown = svg_screen(at, "ending")
    assert 'id="ending-lost-battle"' in shown["svg"]
    assert shown["enabled"] == ["restart"]
    choose(at, "restart", screen="ending")
    assert intro_screen(at) is not None                      # the story from the start
    assert load_game(db_file) == GameState(current_scene="hq", inventory=[])  # a new game


# --- the picture ---

def test_who_goes_first_can_be_clicked_on_the_rappers_or_their_buttons():
    choice = part(STATION, 'id="who-goes-first"', "<!-- end who-goes-first -->")
    assert "WHO GOES FIRST?" in choice
    assert re.search(r'data-overlay="battle-open !rapping', STATION)
    for act_id in ("meyhem_first", "bible_first"):
        assert STATION.count(f'data-action="{act_id}"') >= 2, act_id  # the rapper himself, and a button
    assert 'data-action="bible_finishes"' in STATION


def test_whoever_raps_walks_to_the_mic_and_has_a_skip_button():
    for who, figure in (("meyhem", "MC Meyhem (on the mic"), ("bible", "MC Bible (on the mic")):
        show = part(STATION, f'id="{who}-performs"', f"<!-- end {who}-performs -->")
        assert figure in show, who
        assert 'begin="indefinite"' in show                   # the walk starts when he's up
    for who in ("meyhem", "bible"):
        overlay = STATION[STATION.rindex("<g", 0, STATION.index(f'<g id="{who}-performs"')):]
        assert overlay.startswith(f'<g data-overlay="rapping-{who}"'), who
    skip = part(STATION, 'id="skip-verse"', "<!-- end skip-verse -->")
    assert 'data-action="skip_verse"' in skip and "SKIP" in skip


def test_the_rappers_spots_empty_while_they_rap():
    # changed: "mic-<who>" while he is at the mic (Bible: rapping or choking)
    assert 'data-overlay="!mic-meyhem"' in STATION
    assert 'data-overlay="lacks-rhyme_book !mic-bible"' in STATION


def test_the_game_over_screen():
    # changed: losing used to be a banner in the station; now it is its own game-over screen
    svg = (ROOT / "assets" / "endings" / "ending_lost_battle.svg").read_text()
    assert "KRETE KEEPS THE CROWN" in svg and "GAME OVER" in svg
    assert 'data-action="restart"' in svg and "RESTART" in svg
    assert 'data-action="to_start"' not in svg
    assert 'id="battle-lost"' not in STATION


def test_the_outcome_comes_up_after_the_rapping():
    # changed: a lost battle goes to the game-over screen, so only the winning steps have a sign here
    for act_id in ("meyhem_first", "bible_finishes"):
        assert f'data-overlay="done-{act_id} !rapping"' in STATION, act_id


def test_the_page_tells_the_game_when_a_song_is_over():
    assert "onended" in APP and "audio.end" in APP


# --- Bible without his rhyme book: he chokes, the crowd boos ---

def with_choke_recording(monkeypatch, there):
    path = "audio/mc_bible_verse.mp3" if there else "audio/not_recorded_yet.mp3"
    monkeypatch.setitem(logic.SONGS, "mc_bible_chokes", {"title": "MC Bible chokes", "file": path})


def test_bible_chokes_in_the_app(db_file, monkeypatch):
    with_choke_recording(monkeypatch, there=True)
    at = resume_at(db_file, in_station(rap_battle="meyhem_went_first"))
    act(at, "bible_finishes")
    shown = picture(at)
    assert shown["audio"]["src"] == "app/static/audio/mc_bible_verse.mp3"  # the choke recording
    assert {"rapping", "rapping-bible_chokes", "mic-bible", "booing"} <= set(shown["show"])
    assert "cheering" not in shown["show"]                    # nobody throws their arms up
    assert load_game(db_file).ending == "ending_lost_battle"
    choose(at, "verse_over", screen="picture")
    # changed: when his choke is over, game over (it used to stay in the station)
    assert svg_screen(at, "ending") is not None


def test_until_the_choke_is_recorded_the_outcome_comes_straight_away(db_file, monkeypatch):
    with_choke_recording(monkeypatch, there=False)
    at = resume_at(db_file, in_station())
    act(at, "bible_first")
    assert svg_screen(at, "ending") is not None  # changed: game over straight away
    assert load_game(db_file).rap_battle == "lost"


def test_the_crowd_cheers_for_a_verse(db_file):
    at = resume_at(db_file, in_station())
    act(at, "meyhem_first")
    assert "cheering" in picture(at)["show"] and "booing" not in picture(at)["show"]


def test_the_choke_in_the_picture():
    choke = part(STATION, 'id="bible_chokes-performs"', "<!-- end bible_chokes-performs -->")
    assert "MC Bible (choking" in choke                       # at the mic, no book, sweating
    assert "MC Bible (black leather jacket, pointing)" not in choke and "rhyme book)" not in choke
    boo = part(STATION, 'id="crowd-boos"', "<!-- end crowd-boos -->")
    assert "BOO" in boo
    assert 'data-overlay="booing"' in STATION[STATION.rindex("<g", 0, STATION.index('<g id="crowd-boos"')):][:40]
