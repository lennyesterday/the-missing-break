"""The DJ battle: Needle's set (specs/the-dj-battle.md). With the record and practice, START THE
BATTLE plays Needle's mix of the classics, "Think About It" drops, the club goes off, Portals puts
King Krete's crown on Needle's head, and the GoodFellas win."""

import re
import wave
from pathlib import Path

import pytest

from art import build, needle_mix
from db import load_game, save_game
from logic import DJ_SET, SCENES, SONGS, GameState
from tests.apphelpers import choose, picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
SET = ROOT / "assets" / "screens" / "dj_set.svg"
MIX = ROOT / "static" / "audio" / "records" / "needle_mix.wav"
WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]
CLASSICS = ["apache", "funky_drummer", "its_just_begun", "the_mexican", "vitamin_c", "impeach_the_president"]


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def at_the_battle(db_file, inventory=WITH_RECORD, practiced=True):
    save_game(db_file, GameState(current_scene="battle", inventory=inventory, practiced=practiced))
    at = start_app()
    choose(at, "resume")
    for _ in SCENES["battle"]["dialogue"]:
        choose(at, "next", screen="picture")
    choose(at, "start_battle", screen="picture")
    return at


def appears_at(svg, marker):
    """When the group holding marker first shows (its first begin)."""
    i = svg.index(marker)
    return float(re.search(r'begin="([\d.]+)s"', svg[i:]).group(1))


# --- the mix ---

def test_the_mix_cuts_through_the_classics_then_think_about_it_drops():
    cuts = needle_mix.timeline()
    assert [song for song, _, _ in cuts] == CLASSICS + ["think_about_it"]
    starts = [start for _, start, _ in cuts]
    assert starts == sorted(starts) and starts[0] == 0
    assert all(end > start for _, start, end in cuts)
    assert needle_mix.drop_at() == pytest.approx(starts[-1])


def test_each_break_is_two_bars():
    for song, start, beat, beats in needle_mix.MIX:
        assert song in SONGS and beats == 8 and 0.45 < beat < 0.65  # 92 to 133 BPM


def test_about_forty_seconds():
    assert 38 <= needle_mix.total_secs() <= 44


def test_the_rules_know_the_drop_and_the_length():
    assert DJ_SET["song"] == "needle_mix" and SONGS["needle_mix"]["file"] == "audio/records/needle_mix.wav"
    assert DJ_SET["drop"] == pytest.approx(needle_mix.drop_at(), abs=0.01)
    assert DJ_SET["secs"] == pytest.approx(needle_mix.total_secs(), abs=0.01)


def test_the_mix_is_made():
    with wave.open(str(MIX)) as w:
        secs = w.getnframes() / w.getframerate()
    assert secs == pytest.approx(needle_mix.total_secs(), abs=0.05)


# --- what's said ---

def test_the_lines():
    lines = [(who, line) for who, line, _ in DJ_SET["lines"]]
    assert ("crowd", "YOO! I NEVER HEARD THIS ONE!") in lines
    assert ("bible", "SAY HO!") in lines and ("crowd", "HO!") in lines
    assert ("krete", "HEY! MY CROWN!") in lines
    assert lines[-1] == ("host", "THE GOODFELLAS WIN THE BOROUGH DJ BATTLE!")
    times = [secs for _, _, secs in DJ_SET["lines"]]
    assert times == sorted(times) and all(DJ_SET["drop"] < t < DJ_SET["secs"] for t in times)


# --- the picture ---

def test_the_set_matches_its_source():
    assert SET.read_text() == build.dj_set_screen()


def test_the_picture_goes_on_by_itself_and_can_be_skipped():
    svg = SET.read_text()
    assert 'data-auto-action="set_over"' in svg
    assert float(re.search(r'data-auto-delay="([\d.]+)"', svg).group(1)) >= DJ_SET["secs"]
    assert 'data-action="set_over"' in svg and "SKIP" in svg


def test_the_sign_says_whats_spinning():
    svg = SET.read_text()
    for song, start, _ in needle_mix.timeline():
        title = SONGS[song]["title"].upper()
        assert f"<title>Now spinning: {SONGS[song]['title']}</title>" in svg, song
        assert appears_at(svg, f"<title>Now spinning: {SONGS[song]['title']}</title>") == pytest.approx(start, abs=0.01), song
        assert title.replace("(", "").replace(")", "").split()[0] in svg


def test_a_scratch_at_every_cut():
    assert SET.read_text().count("SCRATCH!") >= len(needle_mix.MIX) - 1


def test_when_think_about_it_drops_the_club_goes_off():
    svg = SET.read_text()
    drop = DJ_SET["drop"]
    for marker in ('id="drop-flash"', 'id="drop-piece"', 'id="crowd-wild"', 'id="bboys-dancing"',
                   'id="reekz-goes-down"', 'id="hype-bible"', 'id="hype-portals"'):
        assert marker in svg, marker
        assert appears_at(svg, marker) >= drop - 0.01, marker
    assert 'class="onlooker cheering"' in svg or "jump" in svg
    assert "reekz-breaking" in svg[svg.index('id="reekz-goes-down"'):]
    assert svg.count("B-boy (toprock") >= 2


def test_portals_puts_kretes_crown_on_needles_head():
    svg = SET.read_text()
    assert 'id="crown"' in svg
    crown = svg[svg.index('id="crown"'):]
    assert "animateMotion" in crown[:3000] or 'type="translate"' in crown[:3000]
    assert appears_at(svg, 'id="portals-snatch"') > DJ_SET["drop"]
    # Krete's own crown is drawn apart, so it can leave his head
    assert svg.count("King Krete (Sopranos MC") == 1


def test_the_lines_have_bubbles_when_theyre_said():
    svg = SET.read_text()
    for who, line, secs in DJ_SET["lines"]:
        title = f"<title>{who}: {line}</title>"
        assert title in svg, line
        assert appears_at(svg, title) == pytest.approx(secs, abs=0.01), line


def test_on_the_legends_ending_needle_wears_the_crown():
    legends = (ROOT / "assets" / "endings" / "ending_legends.svg").read_text()
    assert 'id="needles-crown"' in legends


# --- in the app ---

def test_with_the_record_and_practice_needle_plays_his_set(db_file):
    at = at_the_battle(db_file)
    assert load_game(db_file).ending == "ending_legends"     # saved at once, as before
    shown = svg_screen(at, "dj_set")
    assert shown is not None and 'id="dj-set"' in shown["svg"]
    assert shown["audio"]["src"] == "app/static/audio/records/needle_mix.wav"
    assert shown["audio"]["end"] == "set_over"
    assert "set_over" in shown["enabled"]
    assert svg_screen(at, "ending") is None


def test_after_the_set_the_ending(db_file):
    at = at_the_battle(db_file)
    choose(at, "set_over", screen="dj_set")
    shown = svg_screen(at, "ending")
    assert shown is not None and 'id="ending-legends"' in shown["svg"]
    assert svg_screen(at, "dj_set") is None


def test_after_a_restart_during_the_set_the_ending(db_file):
    at_the_battle(db_file)
    at = start_app()
    choose(at, "resume")
    assert svg_screen(at, "dj_set") is None
    assert 'id="ending-legends"' in svg_screen(at, "ending")["svg"]


@pytest.mark.parametrize("inventory, practiced, ending", [(WITH_RECORD, False, "ending_out_of_practice"),
                                                          ([], False, "ending_static")])
def test_otherwise_no_set(db_file, inventory, practiced, ending):
    at = at_the_battle(db_file, inventory, practiced)
    assert svg_screen(at, "dj_set") is None
    assert f'id="{ending.replace("_", "-")}"' in svg_screen(at, "ending")["svg"]


def test_the_set_speaks_its_recorded_lines(db_file):
    at = at_the_battle(db_file)
    voice = svg_screen(at, "dj_set")["voice"]
    folder = ROOT / "static" / "audio" / "voices" / "battle" / "set"
    recorded = [(i, who, secs) for i, (who, _, secs) in enumerate(DJ_SET["lines"])
                if (folder / f"{i:02d}_{who}.mp3").is_file()]
    if not recorded:
        assert voice is None  # silent until recorded
    else:
        assert [(line["src"], line["delay"]) for line in voice["lines"]] == [
            (f"app/static/audio/voices/battle/set/{i:02d}_{who}.mp3", secs) for i, who, secs in recorded]
    assert picture(at) is None
