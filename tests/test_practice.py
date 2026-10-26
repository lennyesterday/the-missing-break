"""The plot twist: winning "Think About It" back isn't enough. Needle has to go back to the
basement and practice the break before Disco Fever; with the record but out of practice, the
crew still loses (Out of Practice). Practicing is saved."""

import re
import sqlite3
from pathlib import Path

import pytest

from db import load_game, save_game
from logic import ENDINGS, SCENES, GameState, apply_action, available_actions
from tests.apphelpers import act, choose, picture, start_app, svg_screen

ROOT = Path(__file__).parent.parent
HQ = (ROOT / "assets" / "scenes" / "hq.svg").read_text()


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def ids(state):
    return [a["id"] for a in available_actions(state)]


WITH_RECORD = ["rhyme_book", "service_key", "vinyl"]
# changed: practicing for real takes Grandmaster Flash's advice and crayons (test_flash.py)
READY = dict(inventory=WITH_RECORD + ["crayons"], stuck=True, met_flash=True)


# --- the rules ---

def test_a_new_game_has_not_practiced():
    assert GameState().practiced is False


def test_practice_is_offered_in_the_basement_once_the_crew_has_the_record():
    # changed: and once Needle has been to Grandmaster Flash
    assert "practice" not in ids(GameState(current_scene="hq", inventory=["rhyme_book"]))
    assert "practice" not in ids(GameState(current_scene="hq", inventory=WITH_RECORD))
    assert "practice" in ids(GameState(current_scene="hq", **READY))
    assert "practice" not in ids(GameState(current_scene="block", **READY))  # only in the basement


def test_practicing_is_remembered_and_done_once():
    result = apply_action(GameState(current_scene="hq", **READY), "practice")  # changed: with Flash's advice and crayons
    assert result.accepted and result.state.practiced is True
    assert result.state.inventory == READY["inventory"]
    assert "practice" not in ids(result.state)


@pytest.mark.parametrize("inventory, practiced, ending", [
    (WITH_RECORD, True, "ending_legends"),            # the record, and he practiced: the win
    (WITH_RECORD, False, "ending_out_of_practice"),   # the plot twist: the record, but out of practice
    ([], False, "ending_static"),                     # no record at all
])
def test_the_dj_battle_needs_the_record_and_practice(inventory, practiced, ending):
    state = GameState(current_scene="battle", inventory=list(inventory), practiced=practiced)
    assert apply_action(state, "start_battle").state.ending == ending


def test_out_of_practice_is_a_clearly_named_ending():
    assert ENDINGS["ending_out_of_practice"]["title"] == "Out of Practice"
    text = ENDINGS["ending_out_of_practice"]["text"]
    assert "Think About It" in text and "practice" in text.lower()


def test_a_hint_when_the_record_is_won():
    win = next(a for a in SCENES["station"]["actions"] if a["id"] == "rap_battle")  # changed: was "bible_finishes" (specs/remove-meyhem.md)
    assert "hasn't touched it in days" in win["message"]


# --- saving ---

def test_practicing_is_saved(tmp_path):
    path = tmp_path / "game.db"
    save_game(path, GameState(current_scene="hq", inventory=WITH_RECORD, practiced=True))
    assert load_game(path).practiced is True


def test_older_saves_load_not_practiced(tmp_path):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE save (id INTEGER PRIMARY KEY CHECK (id = 1), current_scene TEXT NOT NULL,"
                     " inventory TEXT NOT NULL, ending TEXT, rap_battle TEXT)")
        conn.execute("INSERT INTO save VALUES (1, 'hq', '[]', NULL, NULL)")
    assert load_game(path).practiced is False


# --- in the app ---

def practicing(db_file):
    save_game(db_file, GameState(current_scene="hq", rap_battle="won", **READY))  # changed: Flash's advice, crayons
    at = start_app()
    choose(at, "resume")
    choose(at, "practice", screen="picture")
    return at


def to_the_decks(at):
    """Behind the decks: changed: first he marks the break with the crayon, twice (one mark on
    each copy; each time his hand stops the record, marks it and lets it go: test_flash_scenes.py),
    then he keeps the break going."""
    choose(at, "decks_ready", screen="picture")
    for _ in range(2):
        choose(at, "mark_hit", screen="crayon")
        choose(at, "mark_done", screen="crayon")


def game(at):
    return svg_screen(at, "practice")


def test_needle_goes_behind_the_turntables_first(db_file):
    # changed: practicing used to save right away and show the record from above; now Needle
    # walks behind the decks, then the minigame decides
    at = practicing(db_file)
    shown = picture(at)
    assert {"practicing", "needle-busy"} <= set(shown["show"])
    assert shown["enabled"] == ["decks_ready"]
    assert load_game(db_file).practiced is False          # not yet
    to_the_decks(at)
    assert game(at) is not None and game(at)["file"] == "assets/screens/practice.svg"
    # changed: he practices to the drum break of "Think (About It)" (it used to be the whole song), on a loop
    # (changed again: a WAV now, cut to the first drum hit, so it loops without a gap)
    assert game(at)["audio"]["src"].endswith("think_about_it_break.wav") and game(at)["audio"]["loop"] is True


def test_four_clean_switches_in_a_row_and_he_is_ready(db_file):
    # changed: four clean switches (it was three), each harder than the one before
    at = practicing(db_file)
    to_the_decks(at)
    assert {"deck-1", "streak-0"} <= set(game(at)["show"])
    choose(at, "loop_hit", screen="practice")
    assert {"deck-2", "streak-1", "clean"} <= set(game(at)["show"])   # the other deck takes over
    nonce = game(at)["nonce"]
    choose(at, "loop_hit", screen="practice")
    assert {"deck-1", "streak-2"} <= set(game(at)["show"]) and game(at)["nonce"] != nonce
    choose(at, "loop_hit", screen="practice")
    assert {"deck-2", "streak-3"} <= set(game(at)["show"])
    assert load_game(db_file).practiced is False
    choose(at, "loop_hit", screen="practice")
    assert game(at) is None                                            # done: back in the basement
    assert load_game(db_file).practiced is True
    assert "done-practice" in picture(at)["show"] and "practiced" in picture(at)["show"]
    assert "practice" not in picture(at)["enabled"]
    audio = picture(at)["audio"]
    assert audio["cmd"] == "fade" and audio["src"].endswith("think_about_it_break.wav")  # the break fades out


def test_a_miss_and_the_break_dies(db_file):
    at = practicing(db_file)
    to_the_decks(at)
    choose(at, "loop_hit", screen="practice")
    choose(at, "loop_miss", screen="practice")                         # too early, or it ran out
    assert {"streak-0", "break-died", "deck-2"} <= set(game(at)["show"])
    assert load_game(db_file).practiced is False


def test_stop_practicing_any_time(db_file):
    at = practicing(db_file)
    to_the_decks(at)
    choose(at, "loop_hit", screen="practice")
    choose(at, "stop_practice", screen="practice")
    assert game(at) is None and picture(at) is not None
    assert load_game(db_file).practiced is False                       # nothing saved
    assert "practice" in picture(at)["enabled"]                        # he can practice again


PRACTICE = (ROOT / "assets" / "screens" / "practice.svg").read_text()


def test_the_minigame_screen():
    for overlay in ("deck-1", "deck-2", "streak-0", "streak-4", "clean", "break-died"):  # changed: up to four
        assert f'data-overlay="{overlay}"' in PRACTICE, overlay
    assert "KEEP THE BREAK GOING" in PRACTICE and "SPIN BACK" in PRACTICE
    assert PRACTICE.count("THINK") >= 2                                # two copies of the record
    assert 'data-action="stop_practice"' in PRACTICE


def windows():
    """For each streak (0 to 3 clean so far): how long the green window is, at the end of the round."""
    end = float(re.search(r'<svg[^>]*data-auto-delay="([\d.]+)"', PRACTICE).group(1))
    out = []
    for n in range(4):  # changed: four switches
        level = PRACTICE[PRACTICE.index(f'<g id="spin-back-{n}"'):PRACTICE.index(f"<!-- end spin-back-{n} -->")]
        hit = level[max(0, level.index('data-action="loop_hit"') - 330):level.index('data-action="loop_hit"')]
        early = level[:level.index('data-action="loop_miss"')]
        window = float(re.search(r'to="visible" begin="([\d.]+)s"', hit).group(1))
        assert re.search(rf'to="hidden" begin="{window:.2f}s"', early), n   # before it, pressing is too early
        assert f'data-overlay="streak-{n}"' in PRACTICE[PRACTICE.rindex("<g", 0, PRACTICE.index(f'<g id="spin-back-{n}"')) - 40:PRACTICE.index(f'<g id="spin-back-{n}"')]
        out.append(end - window)
    return out


def test_spin_back_counts_only_right_before_the_break_runs_out():
    # changed: the window is at the end of a longer round (two loops), and it gets smaller
    assert re.search(r'<svg[^>]*data-auto-action="loop_miss"', PRACTICE)   # it ran out
    sizes = windows()
    assert sizes == sorted(sizes, reverse=True) and sizes[0] > sizes[-1]   # harder with every clean switch
    assert 0.7 <= sizes[0] <= 0.9 and 0.3 <= sizes[-1] <= 0.4


def test_in_the_basement_he_goes_behind_the_decks():
    walk = HQ[HQ.index('data-overlay="practicing needle-busy"'):]
    assert 'data-auto-action="decks_ready"' in walk[:200]
    behind = HQ.index('id="needle-behind-decks"')
    assert behind < HQ.index("<!-- the DJ table with two turntables -->")   # drawn behind the table


def test_the_practice_button_in_the_basement():
    # changed: the real practice comes after Flash ("met-flash"); before it Needle tries and can't
    # changed again (specs/battle-preparation.md, part 2): both are started by clicking the turntables,
    # not a PRACTICE THE BREAK button (and not while he's already at it)
    button = HQ[HQ.index('data-action="practice"') - 200:]
    assert 'data-overlay="met-flash !practiced !practicing"' in button[:300] and 'class="turntables-click"' in button[:300]
    first_try = HQ[HQ.index('data-action="try_practice"') - 200:]
    assert 'data-overlay="has-vinyl !stuck !practicing"' in first_try[:300] and 'class="turntables-click"' in first_try[:300]
    assert 'data-overlay="done-practice"' in HQ


def test_the_out_of_practice_ending():
    svg = (ROOT / "assets" / "endings" / "ending_out_of_practice.svg").read_text()
    assert "OUT OF PRACTICE" in svg and 'data-action="to_start"' in svg
    assert "THINK" in svg and "SKRRT" in svg                  # he has the record, but the break skips


def test_the_drum_break_ships_with_the_game():
    # changed: a WAV now (it loops without a gap), cut to start right on the first drum hit
    from logic import SONGS
    song = SONGS["think_about_it_break"]
    assert (ROOT / "static" / song["file"]).is_file() and song["loop"] is True
    assert "think_about_it_break.wav" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()
    assert "loop" not in SONGS["think_about_it"]       # the record itself still plays once


def break_samples():
    import wave
    import numpy as np
    from logic import SONGS
    with wave.open(str(ROOT / "static" / SONGS["think_about_it_break"]["file"])) as w:
        rate, channels = w.getframerate(), w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    return rate, data.reshape(-1, channels).mean(axis=1)


def test_the_drum_break_starts_right_on_the_first_hit():
    import numpy as np
    rate, a = break_samples()
    peak = np.abs(a).max()
    first = np.argmax(np.abs(a) > 0.05 * peak) / rate
    assert first < 0.02                                       # no silence before the drums


def test_the_drum_break_is_a_whole_number_of_its_loop():
    from logic import SONGS
    rate, a = break_samples()
    loop = SONGS["think_about_it_break"]["loop_secs"]
    assert 4.1 < loop < 4.3                                   # two bars at about 114 BPM
    loops = len(a) / rate / loop
    assert abs(loops - round(loops)) < 0.002 and round(loops) == 8  # it wraps right on a loop boundary


def test_one_round_on_a_deck_is_two_loops_of_the_break():
    # changed: two loops (it was one), so a round is a bit longer; the switch still lands on a loop restart
    from logic import SONGS
    round_secs = 2 * SONGS["think_about_it_break"]["loop_secs"]
    svg_tag = PRACTICE[:PRACTICE.index(">")]
    assert f'data-auto-delay="{round_secs:.3f}"' in svg_tag and f'data-loop="{round_secs:.3f}"' in svg_tag
    assert 'data-sync="audio"' in svg_tag                     # the picture follows the music's clock


def test_spin_back_switches_decks_on_the_loop_restart():
    # pressing SPIN BACK only counts the press; the switch happens when the loop starts over
    for action in ("loop_hit", "loop_miss"):
        button = PRACTICE[PRACTICE.index(f'data-action="{action}"') - 30:PRACTICE.index(f'data-action="{action}"') + 120]
        assert 'data-defer="1"' in button, action
    assert 'class="press-hit"' in PRACTICE and 'class="press-miss"' in PRACTICE
    app = (ROOT / "app.py").read_text()
    assert "dataset.defer" in app and "dataset.sync" in app


def test_the_page_loops_a_song_when_asked():
    app = (ROOT / "app.py").read_text()
    assert "player.loop" in app
    assert 'cmd === "fade"' in app  # ... and can fade one out


def test_the_drum_break_is_the_same_loop_over_and_over():
    # the recording fades out near its end; the file is one clean loop of it, repeated, so the
    # break never fades or changes while Needle practices
    import numpy as np
    from logic import SONGS
    rate, a = break_samples()
    n = int(round(SONGS["think_about_it_break"]["loop_secs"] * rate))
    loops = [a[k * n:(k + 1) * n] for k in range(len(a) // n)]
    first = loops[0]
    for k, loop in enumerate(loops[1:], 1):
        assert np.sqrt(np.mean(loop ** 2)) > 0.95 * np.sqrt(np.mean(first ** 2)), k   # no fade
        assert np.abs(loop - first).max() < 0.01, k                                     # the very same loop
