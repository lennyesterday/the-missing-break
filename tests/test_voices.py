"""The crew's voices: each speech bubble plays its line, if a recording exists
(static/audio/voices/<scene>/<number>_<speaker>.mp3)."""

from pathlib import Path

import pytest

from logic import SCENES, WALK_LINES
from tests.apphelpers import act, choose, picture, start_app, start_new_game

ROOT = Path(__file__).parent.parent
VOICES = ROOT / "static" / "audio" / "voices"
# changed: MC Meyhem's lines went to someone else (specs/remove-meyhem.md); they stay silent until
# they are recorded in the new speaker's voice
# changed: Reekz's and Portals' new lines are recorded now (specs/new-voices.md); Bible's two aren't yet
# changed again: Bible's "A RAP BATTLE? BET." is recorded now (specs/dialogue-update.md)
NOT_RECORDED_YET = {"hq/back/01_bible"}


def recorded(folder, i, speaker):
    """Is this line recorded (or one of Meyhem's old lines, not recorded yet)?"""
    name = f"{folder}/{i:02d}_{speaker}"
    return name in NOT_RECORDED_YET or (VOICES / f"{name}.mp3").is_file()


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def lines_for(scene, kind):
    """The lines a voices folder belongs to: <scene>/ the first conversation, <scene>/back/ coming
    back, <scene>/after/ right after being turned down, <scene>/locked/ when it's turned down.
    changed (specs/dialogue-update.md): also <scene>/won/, <scene>/stuck/ and walks/<walk>/ (a line
    said during a walk)."""
    if scene == "walks":
        return [(speaker, line) for speaker, line, _ in WALK_LINES[kind]]
    info = SCENES[scene]
    if kind == "talk":
        return info["dialogue"]
    if kind == "back":
        return info["dialogue_back"]["lines"]
    if kind == "after":
        return [line for lines in info["dialogue_after"].values() for line in lines]
    if kind in ("won", "stuck"):
        return info[f"dialogue_{kind}"]["lines"]
    return [line for action in info["actions"] for line in action.get("locked_says", [])]


def test_every_recording_belongs_to_a_line_and_its_speaker():
    # changed: the conversations for coming back, being turned down and right after it have their
    # own folders (specs/story-line-fixes.md, specs/story-line-fixes-2.md); the gate only has those
    for f in VOICES.rglob("*.mp3"):
        scene, *kind = f.parent.relative_to(VOICES).parts
        lines = lines_for(scene, kind[0] if kind else "talk")
        number, speaker = f.stem.split("_", 1)
        assert lines[int(number)][0] == speaker, f


def test_needle_and_bible_are_recorded():
    assert (VOICES / "hq" / "00_needle.mp3").is_file()
    assert (VOICES / "hq" / "01_bible.mp3").is_file()


def test_needle_speaks_when_the_basement_appears(db_file):
    at = start_app()
    start_new_game(at)
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/hq/00_needle.mp3"


def test_the_click_to_the_next_bubble_plays_bible(db_file):
    at = start_app()
    start_new_game(at)
    first = picture(at)["voice"]
    choose(at, "next", screen="picture")
    voice = picture(at)["voice"]
    assert voice["src"] == "app/static/audio/voices/hq/01_bible.mp3" and voice["id"] != first["id"]


def test_a_line_without_a_recording_is_silent(db_file):
    # changed: every basement line is recorded now, so this checks a scene without recordings
    # changed: the block is recorded now too, so Rico's shop (no recordings yet)
    # changed: Rico's shop is recorded now too, so the station (no recordings yet)
    # changed: the station is recorded now too, except Bible's last line (specs/new-voices.md)
    # changed: that one is recorded now too (specs/dialogue-update.md), so Bible coming back to the
    # basement, the last line without a recording
    from db import save_game
    from logic import GameState
    save_game(db_file, GameState(current_scene="hq", left_scenes=["hq"]))
    at = start_app()
    choose(at, "resume")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/hq/back/00_needle.mp3"
    choose(at, "next", screen="picture")
    assert picture(at)["show"][0] == "back-1" and picture(at)["voice"] is None  # Bible: "WE REALLY SHOULD GO TO RICO'S..."


def test_no_voice_after_leaving(db_file):
    at = start_app()
    start_new_game(at)
    act(at, "go_block")
    assert picture(at)["voice"] is None or "voices/hq" not in picture(at)["voice"]["src"]


def test_the_page_plays_voices_and_lowers_the_background_meanwhile():
    app = (ROOT / "app.py").read_text()
    assert "data.voice" in app and "ended" in app


def test_the_whole_basement_conversation_is_recorded():
    lines = SCENES["hq"]["dialogue"]
    for i, (speaker, _) in enumerate(lines):
        assert recorded("hq", i, speaker), (i, speaker)  # changed: see NOT_RECORDED_YET


def test_the_whole_block_conversation_is_recorded():
    lines = SCENES["block"]["dialogue"]
    for i, (speaker, _) in enumerate(lines):
        assert recorded("block", i, speaker), (i, speaker)  # changed: see NOT_RECORDED_YET


def test_portals_speaks_when_the_block_appears(db_file):
    from db import save_game
    from logic import GameState
    save_game(db_file, GameState(current_scene="block", inventory=[]))
    at = start_app()
    choose(at, "resume")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/block/00_portals.mp3"


def test_the_whole_record_shop_conversation_is_recorded():
    lines = SCENES["record_shop"]["dialogue"]
    for i, (speaker, _) in enumerate(lines):
        assert recorded("record_shop", i, speaker), (i, speaker)  # changed: see NOT_RECORDED_YET


def test_the_whole_station_conversation_is_recorded():
    for i, (speaker, _) in enumerate(SCENES["station"]["dialogue"]):
        assert recorded("station", i, speaker), (i, speaker)


def test_krete_speaks_when_the_crew_comes_in(db_file):
    from db import save_game
    from logic import GameState
    save_game(db_file, GameState(current_scene="station", inventory=["service_key"]))
    at = start_app()
    choose(at, "resume")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/station/00_krete.mp3"


def test_the_lines_meyhem_gave_away_are_spoken_now():
    for name in ("hq/03_reekz", "hq/08_portals", "record_shop/05_reekz", "block/02_portals"):
        assert (VOICES / f"{name}.mp3").is_file(), name


def test_rico_speaks_when_the_crew_comes_in(db_file):
    from db import save_game
    from logic import GameState
    save_game(db_file, GameState(current_scene="record_shop", inventory=[]))
    at = start_app()
    choose(at, "resume")
    assert picture(at)["voice"]["src"] == "app/static/audio/voices/record_shop/00_rico.mp3"


def test_every_line_is_spoken_in_turn(db_file):
    at = start_app()
    start_new_game(at)
    heard = []
    for i, (speaker, _) in enumerate(SCENES["hq"]["dialogue"]):
        heard.append((picture(at)["voice"] or {}).get("src"))
        choose(at, "next", screen="picture")
    # changed: Meyhem's old lines are silent until they are recorded again (NOT_RECORDED_YET)
    assert heard == [None if f"hq/{i:02d}_{s}" in NOT_RECORDED_YET else f"app/static/audio/voices/hq/{i:02d}_{s}.mp3"
                     for i, (s, _) in enumerate(SCENES["hq"]["dialogue"])]
    assert picture(at)["voice"] is None  # the conversation is over


def test_the_texts_match_the_recordings():
    texts = [line for _, line in SCENES["hq"]["dialogue"]]
    assert texts[2] == "YO! THAT SHIT IS CRAZY, DAWG. THE CRATE IS EMPTY!"  # changed: edited by the product owner
    assert texts[4] == "THEY WENT OVER OUR PIECE. THAT'S DISRESPECTFUL, SON!"
    assert texts[5] == 'THEY TOOK "THINK ABOUT IT", MY SECRET BREAK FOR THE FINAL!'
    assert texts[7] == "FIRST I NEED MY RHYME BOOK TO WRITE A DISS FOR KRETE. IT'S ON THE COUCH."
