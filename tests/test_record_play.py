"""In the basement: click a classic on the floor, Needle walks over, picks it up, puts it on the
turntable, and the picture switches to the turntable seen from above, playing that record."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game
from logic import RECORDS
from tests.apphelpers import choose, picture, start_app, start_new_game, svg_screen

ROOT = Path(__file__).parent.parent
HQ = ROOT / "assets" / "scenes" / "hq.svg"
# changed: Scorpio was swapped for CAN's Vitamin C
CLASSICS = ["apache", "funky_drummer", "its_just_begun", "impeach_the_president", "vitamin_c", "the_mexican"]


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def part(svg, start, end):
    piece = svg[svg.index(start):]
    return piece[:piece.index(end)]


def test_the_classics_are_story_content():
    # changed: "Think (About It)" joined them; it can be played once the crew has won it back
    assert list(RECORDS) == CLASSICS + ["think_about_it"]
    for record in RECORDS.values():
        assert {"title", "artist", "year", "song"} <= set(record)
    assert RECORDS["apache"]["artist"] == "Incredible Bongo Band"


def test_the_sound_system_is_smaller():
    system = part(HQ.read_text(), 'id="soundsystem"', ">")
    # changed: smaller again (it was 0.7), so it no longer stands on the records (see test_basement_layout)
    assert float(re.search(r"scale\(([\d.]+)\)", system).group(1)) <= 0.5


def test_comic_posters_on_the_wall():
    posters = part(HQ.read_text(), 'id="comic-posters"', "<!-- end comic-posters -->")
    assert posters.count('class="comic-poster"') == 3
    for title in ("B-BOY BLASTER", "SPRAY CAN KID", "BLOCK PARTY"):
        assert title in posters


@pytest.mark.parametrize("record", CLASSICS)
def test_every_sleeve_can_be_clicked_and_leaves_the_floor_while_needle_has_it(record):
    svg = HQ.read_text()
    assert f'data-action="pick:{record}"' in svg
    assert f'data-overlay="!pick-{record}"' in svg           # the sleeve is gone from the floor meanwhile
    walk = part(svg, f'data-overlay="needle-busy pick-{record}"', f"<!-- end pick-{record} -->")
    assert f'id="pick_{record}"' in walk and 'begin="indefinite"' in walk
    assert "<!-- Fantastic Needle" in walk                    # Needle walks, picks it up, carries it
    assert walk.count('attributeName="visibility" to="visible"') >= 3
    assert 'class="spinning-record"' in walk                  # it ends up on the turntable
    assert f'data-auto-action="play_record:{record}"' in walk  # then the picture switches by itself


@pytest.mark.parametrize("record", CLASSICS)
def test_the_turntable_from_above(record):
    svg = (ROOT / "assets" / "records" / f"{record}.svg").read_text()
    info = RECORDS[record]
    assert 'id="turntable-top"' in svg
    assert 'type="rotate"' in svg                     # the record spins (seen from above it's round)
    assert 'id="tonearm"' in svg
    assert info["title"].upper() in svg and info["artist"].upper() in svg and str(info["year"]) in svg
    assert "NOW PLAYING" in svg and 'data-action="back"' in svg
    assert (ROOT / "assets" / "records" / f"{record}.svg").read_text() == build.turntable_screen(record)


def test_pick_play_and_back(db_file):
    at = start_app()
    start_new_game(at)
    saved = load_game(db_file)
    assert "pick:apache" in picture(at)["enabled"]

    choose(at, "pick:apache", screen="picture")
    shown = picture(at)
    assert {"needle-busy", "pick-apache"} <= set(shown["show"])
    assert shown["enabled"] == ["play_record:apache"]  # Needle is busy: nothing else meanwhile

    choose(at, "play_record:apache", screen="picture")
    assert picture(at) is None
    turntable = svg_screen(at, "turntable")
    # changed: the turntable's START / STOP button works too (pause and continue)
    assert 'id="record-apache"' in turntable["svg"] and turntable["enabled"] == ["back", "toggle_play"]

    choose(at, "back", screen="turntable")
    assert svg_screen(at, "turntable") is None
    assert "needle-busy" not in picture(at)["show"]
    assert load_game(db_file) == saved  # listening to records is not a move


def test_the_page_can_trigger_an_action_by_itself():
    app = (ROOT / "app.py").read_text()
    assert "data-auto-action" in app and "setTimeout" in app


@pytest.mark.parametrize("record", CLASSICS)
def test_every_classic_has_its_song(record):
    from logic import SONGS
    song = SONGS[RECORDS[record]["song"]]
    assert (ROOT / "static" / song["file"]).is_file()
    assert RECORDS[record]["title"] in song["title"]
    assert "COMING SOON" not in (ROOT / "assets" / "records" / f"{record}.svg").read_text()


def test_scorpio_is_gone():
    assert "scorpio" not in RECORDS
    assert "SCORPIO" not in HQ.read_text()


def test_the_song_plays_on_the_turntable_and_stops_on_back(db_file):
    at = start_app()
    start_new_game(at)
    choose(at, "pick:vitamin_c", screen="picture")
    choose(at, "play_record:vitamin_c", screen="picture")
    playing = svg_screen(at, "turntable")["audio"]
    assert playing["src"] == "app/static/audio/records/vitamin_c.mp3"

    choose(at, "back", screen="turntable")
    stopped = picture(at)["audio"]
    assert stopped["src"] is None and stopped["id"] != playing["id"]  # a new instruction: stop


def test_the_page_can_stop_a_song():
    app = (ROOT / "app.py").read_text()
    assert "pause()" in app


# --- pause and continue with START, and the song always stops when leaving the turntable ---

def on_the_turntable(db_file, record="apache"):
    at = start_app()
    start_new_game(at)
    choose(at, f"pick:{record}", screen="picture")
    choose(at, f"play_record:{record}", screen="picture")
    return at


def test_the_start_button_pauses_and_continues(db_file):
    at = on_the_turntable(db_file)
    shown = svg_screen(at, "turntable")
    assert "toggle_play" in shown["enabled"] and shown["show"] == []
    playing = shown["audio"]

    choose(at, "toggle_play", screen="turntable")
    paused = svg_screen(at, "turntable")
    assert paused["show"] == ["paused"]
    assert paused["audio"]["cmd"] == "pause" and paused["audio"]["id"] != playing["id"]

    choose(at, "toggle_play", screen="turntable")
    again = svg_screen(at, "turntable")
    assert again["show"] == []
    assert again["audio"]["cmd"] == "resume"  # continues where it stopped, not from the start


def test_back_stops_the_song_even_when_paused(db_file):
    at = on_the_turntable(db_file)
    choose(at, "toggle_play", screen="turntable")
    choose(at, "back", screen="turntable")
    assert picture(at)["audio"]["src"] is None
    # the next record starts playing (not paused)
    choose(at, "pick:funky_drummer", screen="picture")
    choose(at, "play_record:funky_drummer", screen="picture")
    assert svg_screen(at, "turntable")["show"] == []


@pytest.mark.parametrize("record", CLASSICS + ["think_about_it"])
def test_every_turntable_has_a_start_button_and_a_paused_sign(record):
    svg = (ROOT / "assets" / "records" / f"{record}.svg").read_text()
    button = part(svg, 'data-action="toggle_play"', "</g>")
    assert "START" in button
    assert 'data-overlay="paused"' in svg and "PAUSED" in svg


def test_the_page_pauses_resumes_and_stops_when_the_turntable_goes():
    app = (ROOT / "app.py").read_text()
    assert 'cmd === "pause"' in app and 'cmd === "resume"' in app
    assert "pauseAnimations" in app and "unpauseAnimations" in app
    assert 'startsWith("assets/records/")' in app  # leaving the turntable view stops its record
