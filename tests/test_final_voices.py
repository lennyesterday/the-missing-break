"""Final voices (specs/final-voices.md): the block before the final, the walk to the Borough DJ
Battle (King Krete, then the bouncer) and battle night are spoken."""

import re
from pathlib import Path

import pytest

from db import save_game
from logic import SCENES, WALK_LINES, GameState
from tests.apphelpers import act, choose, picture, start_app

ROOT = Path(__file__).parent.parent
VOICES = ROOT / "static" / "audio" / "voices"
WALK = ROOT / "assets" / "walks" / "block__battle.svg"


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def final_lines():
    return next(m for m in SCENES["block"]["moments"] if m["kind"] == "final")["lines"]


# --- the recordings ---

def test_the_block_before_the_final_is_recorded():
    for i, (speaker, _) in enumerate(final_lines()):
        assert (VOICES / "block" / "final" / f"{i:02d}_{speaker}.mp3").is_file(), (i, speaker)


def test_battle_night_is_recorded():
    for i, (speaker, _) in enumerate(SCENES["battle"]["dialogue"]):
        assert (VOICES / "battle" / f"{i:02d}_{speaker}.mp3").is_file(), (i, speaker)


def test_the_walk_to_the_club_has_krete_then_the_bouncer():
    lines = WALK_LINES["block__battle"]
    assert [(speaker, line) for speaker, line, _ in lines] == [
        ("krete", "BACK FOR MORE, GOODFELLAS? DIDN'T LEARN THE FIRST TIME?"),
        ("bouncer", "GOODFELLAS! GO ON IN.")]
    (_, _, krete_at), (_, _, bouncer_at) = lines
    assert bouncer_at - krete_at >= 4.3  # Krete's recording is about 4.3 s: the bouncer waits for him
    for i, (speaker, _, _) in enumerate(lines):
        assert (VOICES / "walks" / "block__battle" / f"{i:02d}_{speaker}.mp3").is_file(), (i, speaker)


# --- the picture of the walk ---

def begins(svg, title):
    """When the bubble with this title shows, and when it goes (None: it stays)."""
    start = svg.rindex("<g", 0, svg.index(f"<title>{title}"))
    bubble = svg[start:svg.index("</g>", start)]
    times = [float(t) for t in re.findall(r'to="(?:0|1)" begin="([\d.]+)s"', bubble)]
    return times[0], (times[1] if len(times) > 1 else None)


def test_the_bubbles_show_when_the_lines_are_said():
    svg = WALK.read_text()
    (_, _, krete_at), (_, _, bouncer_at) = WALK_LINES["block__battle"]
    shows, goes = begins(svg, "King Krete: BACK FOR MORE")
    assert shows == pytest.approx(krete_at) and goes >= krete_at + 4.3  # up as long as he talks
    shows, _ = begins(svg, "Bouncer: GOODFELLAS! GO ON IN.")
    assert shows == pytest.approx(bouncer_at)


def test_the_bouncer_lifts_the_rope_after_he_speaks():
    from art import build
    (_, _, bouncer_at) = WALK_LINES["block__battle"][1]
    assert build.ROPE_OPENS > bouncer_at
    rope = WALK.read_text().split('id="velvet-rope"', 1)[1]
    assert f'begin="{build.ROPE_OPENS:.2f}s"' in rope[:2000]


# --- in the app ---

def test_on_the_walk_krete_and_the_bouncer_speak_in_turn(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=[]))
    at = start_app()
    choose(at, "resume")
    choose(at, "go_battle", screen="picture")
    voice = picture(at)["voice"]
    assert [(line["src"], line["delay"]) for line in voice["lines"]] == [
        (f"app/static/audio/voices/walks/block__battle/{i:02d}_{speaker}.mp3", secs)
        for i, (speaker, _, secs) in enumerate(WALK_LINES["block__battle"])]


def test_battle_night_speaks_in_turn(db_file):
    save_game(db_file, GameState(current_scene="block", inventory=[]))
    at = start_app()
    choose(at, "resume")
    act(at, "go_battle")
    choose(at, "enter", screen="picture")
    for i, (speaker, _) in enumerate(SCENES["battle"]["dialogue"]):
        assert picture(at)["voice"]["src"] == f"app/static/audio/voices/battle/{i:02d}_{speaker}.mp3"
        choose(at, "next", screen="picture")
    assert picture(at)["voice"] is None


def test_the_page_plays_each_line_of_a_walk():
    app = (ROOT / "app.py").read_text()
    assert "data.voice.lines" in app
