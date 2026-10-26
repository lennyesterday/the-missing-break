"""The rap battle: Bible alone on the mic (MC Meyhem is gone, see specs/remove-meyhem.md). With his
rhyme book he wins the record; without it he chokes, the crowd boos and the game is over. Verses
can be skipped and stop when the crew leaves the station.

(Replaces tests/test_rap_order.py, which tested who goes first: Meyhem, then Bible.)"""

import sqlite3
from pathlib import Path

import pytest

import logic
from db import load_game, save_game
from logic import CHOKED_MESSAGE, ENDINGS, RAPPERS, SCENES, SONGS, GameState, apply_action, available_actions, new_game, what_happens
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


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


# --- the rules ---

def test_a_new_game_has_not_battled_yet():
    assert new_game().rap_battle is None


def test_one_choice_rap_battle():
    assert set(ids(in_station())) == {"rap_battle", "go_block"}


def test_with_his_rhyme_book_bible_wins_the_record():
    result = apply_action(in_station(("rhyme_book", "service_key")), "rap_battle")
    assert result.accepted
    assert result.state.inventory == ["rhyme_book", "service_key", "vinyl"]
    assert result.state.rap_battle == "won"
    assert ids(result.state) == ["go_block"]  # the record can be won only once


def test_without_his_rhyme_book_bible_chokes_and_the_game_is_over():
    result = apply_action(in_station(), "rap_battle")
    assert result.accepted and result.message == CHOKED_MESSAGE
    assert result.state.rap_battle == "lost" and result.state.ending == "ending_lost_battle"
    assert "vinyl" not in result.state.inventory
    assert ids(result.state) == []
    assert not apply_action(result.state, "go_block").accepted
    assert ENDINGS["ending_lost_battle"]["title"] == "Krete Keeps the Crown"


def test_what_happens_says_who_raps():
    assert what_happens(in_station(("rhyme_book",)), "rap_battle")["raps"] == ["bible"]
    assert what_happens(in_station(), "rap_battle")["raps"] == ["bible_chokes"]
    assert what_happens(in_station(), "rap_battle")["done"] == "bible_chokes"


def test_only_bible_raps():
    assert RAPPERS == {"bible": "mc_bible_verse", "bible_chokes": "mc_bible_chokes"}
    assert "mc_meyhem_verse" not in SONGS
    assert not (ROOT / "static" / "audio" / "mc_meyhem_verse.mp3").exists()


def test_bible_takes_the_battle_without_a_word_about_his_rhyme_book():
    # the player has to remember the book themselves: without it Bible still steps up, and chokes
    lines = SCENES["station"]["dialogue"]
    assert ("bible", "A RAP BATTLE? BET.") in lines
    assert "RHYME BOOK" not in " ".join(line for _, line in lines)


def test_bible_joins_with_or_without_his_rhyme_book():
    assert "rap_battle" in ids(in_station(("rhyme_book", "service_key")))
    assert "rap_battle" in ids(in_station())


# --- saving ---

def test_the_battle_is_saved(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, in_station(rap_battle="lost"))
    assert load_game(path).rap_battle == "lost"


def test_a_save_from_the_middle_of_the_old_battle_opens_it_again(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, in_station(rap_battle="meyhem_went_first"))
    assert load_game(path).rap_battle is None
    assert "rap_battle" in ids(load_game(path))


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


def test_bible_raps_and_can_be_skipped(db_file):
    at = resume_at(db_file, in_station(("rhyme_book", "service_key")))
    act(at, "rap_battle")
    shown = picture(at)
    assert shown["audio"]["src"] == f"app/static/{SONGS['mc_bible_verse']['file']}"
    assert shown["audio"]["end"] == "verse_over"
    assert {"rapping", "rapping-bible", "mic-bible", "cheering"} <= set(shown["show"])
    assert {"skip_verse", "go_block"} <= set(shown["enabled"])
    assert load_game(db_file).rap_battle == "won"
    choose(at, "skip_verse", screen="picture")
    shown = picture(at)
    assert shown["audio"]["src"] is None and "rapping" not in shown["show"]
    assert "done-rap_battle" in shown["show"]


def test_leaving_the_station_stops_the_verse(db_file):
    at = resume_at(db_file, in_station(("rhyme_book", "service_key")))
    act(at, "rap_battle")
    act(at, "go_block")
    shown = picture(at)
    assert shown["audio"]["src"] is None and "rapping" not in shown["show"]
    assert load_game(db_file).current_scene == "block"


def test_the_battle_state_is_in_the_picture(db_file):
    assert "battle-open" in picture(resume_at(db_file, in_station()))["show"]


def test_lost_means_game_over_and_restart_starts_again_from_the_intro(db_file):
    lost = GameState(current_scene="station", inventory=["service_key"], ending="ending_lost_battle", rap_battle="lost")
    at = resume_at(db_file, lost)
    shown = svg_screen(at, "ending")
    assert 'id="ending-lost-battle"' in shown["svg"]
    assert shown["enabled"] == ["restart"]
    assert "lost-choked" in shown["show"]
    choose(at, "restart", screen="ending")
    assert intro_screen(at) is not None
    assert load_game(db_file) == GameState(current_scene="hq", inventory=[])


def with_choke_recording(monkeypatch, there):
    path = "audio/mc_bible_verse.mp3" if there else "audio/not_recorded_yet.mp3"
    monkeypatch.setitem(logic.SONGS, "mc_bible_chokes", {"title": "MC Bible chokes", "file": path})


def test_bible_chokes_in_the_app(db_file, monkeypatch):
    with_choke_recording(monkeypatch, there=True)
    at = resume_at(db_file, in_station())
    act(at, "rap_battle")
    shown = picture(at)
    assert shown["audio"]["src"] == "app/static/audio/mc_bible_verse.mp3"
    assert {"rapping", "rapping-bible_chokes", "mic-bible", "booing"} <= set(shown["show"])
    assert "cheering" not in shown["show"]
    assert load_game(db_file).ending == "ending_lost_battle"
    choose(at, "verse_over", screen="picture")
    assert svg_screen(at, "ending") is not None


def test_until_the_choke_is_recorded_the_outcome_comes_straight_away(db_file, monkeypatch):
    with_choke_recording(monkeypatch, there=False)
    at = resume_at(db_file, in_station())
    act(at, "rap_battle")
    assert svg_screen(at, "ending") is not None
    assert load_game(db_file).rap_battle == "lost"


def test_the_page_tells_the_game_when_a_song_is_over():
    assert "onended" in APP and "audio.end" in APP


# --- the picture ---

def test_the_battle_is_clicked_on_bible_or_the_mic():
    choice = part(STATION, 'id="rap-battle"', "<!-- end rap-battle -->")
    assert 'data-overlay="battle-open !rapping"' in STATION[STATION.rindex("<g", 0, STATION.index('<g id="rap-battle"')):][:60]
    assert choice.count('data-action="rap_battle"') == 2  # Bible himself, and the mic
    assert "RAP BATTLE" in choice
    assert "WHO GOES FIRST" not in STATION


def test_bible_walks_to_the_mic_and_there_is_a_skip_button():
    show = part(STATION, 'id="bible-performs"', "<!-- end bible-performs -->")
    assert "MC Bible (on the mic" in show and 'begin="indefinite"' in show
    skip = part(STATION, 'id="skip-verse"', "<!-- end skip-verse -->")
    assert 'data-action="skip_verse"' in skip and "SKIP" in skip
    assert 'data-overlay="lacks-rhyme_book !mic-bible"' in STATION


def test_the_outcome_comes_up_after_the_rapping():
    assert 'data-overlay="done-rap_battle !rapping"' in STATION


def test_the_choke_in_the_picture():
    choke = part(STATION, 'id="bible_chokes-performs"', "<!-- end bible_chokes-performs -->")
    assert "MC Bible (choking" in choke
    boo = part(STATION, 'id="crowd-boos"', "<!-- end crowd-boos -->")
    assert "BOO" in boo


def test_the_game_over_screen_only_knows_the_choke():
    svg = (ROOT / "assets" / "endings" / "ending_lost_battle.svg").read_text()
    assert "KRETE KEEPS THE CROWN" in svg and "GAME OVER" in svg and 'data-action="restart"' in svg
    assert "lost-order" not in svg and "lost-choked" in svg
